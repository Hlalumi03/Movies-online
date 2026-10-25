const moviesEl = document.getElementById('movies');
const btnSearch = document.getElementById('btnSearch');
const searchInput = document.getElementById('search');
const categorySelect = document.getElementById('category');
const minRatingSelect = document.getElementById('minRating');
const yearSelect = document.getElementById('year');
const statusEl = document.getElementById('status');
const resultCountEl = document.getElementById('resultCount');
const recommendationsEl = document.getElementById('recommendations');
const previousPageButton = document.getElementById('previousPage');
const nextPageButton = document.getElementById('nextPage');
const pageNumberEl = document.getElementById('pageNumber');
const detailsDialog = document.getElementById('movieDialog');
const detailsContent = document.getElementById('movieDetails');
const closeDetailsButton = document.getElementById('closeDetails');
const recommendationSection = document.getElementById('recommendationSection');

const pageSize = 10;
const popularCategories = [
  'Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary',
  'Drama', 'Family', 'Fantasy', 'History', 'Horror', 'Music', 'Mystery',
  'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western',
];
let currentPage = 1;
let totalMovies = 0;
let searchTimer;
let activeSearch;
let recommendedMovies = [];

async function requestJson(url, options) {
  const response = await fetch(url, options);
  const result = await response.json();
  if (!response.ok) {
    const detail = Array.isArray(result.detail)
      ? result.detail.map((error) => error.msg).join(', ')
      : result.detail;
    throw new Error(detail || `Request failed (${response.status})`);
  }
  return result;
}

function setStatus(message) {
  statusEl.textContent = message;
  statusEl.hidden = !message;
}

function makeElement(tagName, className, text) {
  const element = document.createElement(tagName);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

async function loadCategories() {
  const categories = await requestJson('/api/categories');
  categorySelect.replaceChildren(new Option('All categories', ''));
  const knownNames = new Map(popularCategories.map((name) => [name.toLocaleLowerCase(), name]));
  categories.forEach((category) => {
    knownNames.set(category.name.toLocaleLowerCase(), category.name);
  });
  [...knownNames.values()].sort((a, b) => a.localeCompare(b)).forEach((name) => {
    categorySelect.add(new Option(name, name));
  });
}

async function loadYears() {
  const filters = await requestJson('/api/movie-filters');
  yearSelect.replaceChildren(new Option('Any year', ''));
  filters.years.forEach((year) => {
    yearSelect.add(new Option(String(year), String(year)));
  });
}

function movieCard(movie) {
  const posterStyles = [
    'from-violet-900 via-indigo-800 to-slate-950',
    'from-rose-900 via-fuchsia-900 to-slate-950',
    'from-amber-900 via-orange-900 to-slate-950',
    'from-cyan-900 via-blue-900 to-slate-950',
  ];
  const posterStyle = posterStyles[movie.id % posterStyles.length];
  const genre = movie.categories[0]?.name || 'Movie';
  const card = makeElement('article', 'movie-card group flex flex-col overflow-hidden rounded-2xl border border-white/10 bg-white/[0.045] shadow-xl shadow-black/20');
  const poster = makeElement('div', `relative flex min-h-40 flex-col justify-between overflow-hidden bg-gradient-to-br ${posterStyle} p-5`);
  poster.setAttribute('aria-hidden', 'true');
  poster.append(makeElement('span', 'absolute -right-8 -top-10 h-36 w-36 rounded-full border-[22px] border-white/[0.07]'));
  poster.append(makeElement('span', 'absolute -bottom-12 left-1/3 h-32 w-32 rounded-full bg-white/[0.06] blur-xl'));
  const posterHeader = makeElement('div', 'relative flex items-center justify-between gap-2');
  posterHeader.append(makeElement('span', 'rounded-full border border-white/20 bg-black/20 px-3 py-1 text-xs font-semibold text-white/90', genre));
  posterHeader.append(makeElement('span', 'text-sm font-semibold text-white/70', String(movie.year ?? '')));
  poster.append(posterHeader);
  poster.append(makeElement('span', 'relative mt-8 text-xs font-bold uppercase tracking-[0.22em] text-white/50', 'Movie night starts here'));
  card.append(poster);

  const content = makeElement('div', 'flex flex-1 flex-col p-4 sm:p-5');
  const title = makeElement('h3', 'line-clamp-1 text-lg font-bold tracking-tight transition group-hover:text-violet-200', movie.title);
  content.append(title);
  content.append(makeElement('p', 'mt-2 line-clamp-3 min-h-[4.5rem] flex-1 text-sm leading-6 text-indigo-100/65', movie.description || 'No description provided.'));

  const metadata = makeElement('div', 'mt-4 flex flex-wrap items-center gap-2');
  metadata.append(makeElement('span', 'rounded-lg bg-amber-300/10 px-2.5 py-1 text-sm font-bold text-amber-200', `★ ${movie.avg_rating.toFixed(1)}`));
  movie.categories.slice(0, 2).forEach((category) => {
    metadata.append(makeElement('span', 'rounded-lg bg-white/[0.07] px-2.5 py-1 text-xs text-indigo-100/75', category.name));
  });
  content.append(metadata);

  const detailsButton = makeElement('button', 'mt-5 flex w-full items-center justify-center gap-2 rounded-xl border border-violet-300/20 bg-violet-400/10 px-4 py-3 text-sm font-bold text-violet-100 transition hover:border-violet-300/40 hover:bg-violet-400/20', 'View details and reviews');
  detailsButton.type = 'button';
  content.append(detailsButton);
  detailsButton.addEventListener('click', () => openMovieDetails(movie.id));
  card.append(content);
  return card;
}

async function loadRecommendations() {
  recommendationsEl.setAttribute('aria-busy', 'true');
  try {
    recommendedMovies = await requestJson('/api/recommendations');
    renderRecommendations();
  } catch (error) {
    recommendationSection.hidden = true;
    setStatus(`Could not load recommendations: ${error.message}`);
  } finally {
    recommendationsEl.removeAttribute('aria-busy');
  }
}

function renderRecommendations(excludedMovieIds = []) {
  const excludedIds = new Set(excludedMovieIds);
  const visibleRecommendations = recommendedMovies.filter((movie) => !excludedIds.has(movie.id));
  recommendationsEl.replaceChildren();
  recommendationSection.hidden = visibleRecommendations.length === 0;
  visibleRecommendations.forEach((movie) => recommendationsEl.append(movieCard(movie)));
}

async function search(resetPage = false) {
  if (resetPage) currentPage = 1;
  if (activeSearch) activeSearch.abort();
  activeSearch = new AbortController();
  const { signal } = activeSearch;
  btnSearch.disabled = true;
  btnSearch.textContent = 'Searching…';
  setStatus('Searching movies…');

  const params = new URLSearchParams({
    page: String(currentPage),
    per_page: String(pageSize),
  });
  const query = searchInput.value.trim();
  if (query) params.set('q', query);
  if (categorySelect.value) params.set('category', categorySelect.value);
  if (minRatingSelect.value) params.set('min_rating', minRatingSelect.value);
  if (yearSelect.value) params.set('year', yearSelect.value);

  try {
    const result = await requestJson(`/api/movies?${params}`, { signal });
    if (signal.aborted) return;
    totalMovies = result.total;
    resultCountEl.textContent = `${totalMovies} movie${totalMovies === 1 ? '' : 's'} found`;
    pageNumberEl.textContent = `Page ${result.page}`;
    previousPageButton.disabled = result.page <= 1;
    nextPageButton.disabled = result.page * result.per_page >= result.total;
    moviesEl.replaceChildren();
    renderRecommendations(result.items.map((movie) => movie.id));
    setStatus('');

    if (result.items.length === 0) {
      moviesEl.append(makeElement('p', 'text-center text-indigo-200 md:col-span-3', 'No movies found.'));
      return;
    }
    result.items.forEach((movie) => moviesEl.append(movieCard(movie)));
  } catch (error) {
    if (error.name === 'AbortError') return;
    moviesEl.replaceChildren();
    resultCountEl.textContent = '';
    setStatus(`Could not load movies: ${error.message}`);
  } finally {
    if (!signal.aborted) {
      btnSearch.disabled = false;
      btnSearch.textContent = 'Search movies';
    }
  }
}

function reviewForm(movieId) {
  const form = makeElement('form', 'mt-6 space-y-3');
  const heading = makeElement('h3', 'text-lg font-semibold', 'Write a review');
  const ratingLabel = makeElement('label', 'block text-sm', 'Rating (1 to 5)');
  ratingLabel.htmlFor = 'reviewRating';
  const rating = makeElement('select', 'mt-1 block w-full p-2 rounded bg-indigo-950');
  rating.id = 'reviewRating';
  rating.required = true;
  for (let value = 5; value >= 1; value -= 1) {
    rating.add(new Option(`${value} star${value === 1 ? '' : 's'}`, String(value)));
  }
  const textLabel = makeElement('label', 'block text-sm', 'Your review (optional)');
  textLabel.htmlFor = 'reviewText';
  const text = makeElement('textarea', 'mt-1 block w-full p-2 rounded bg-indigo-950');
  text.id = 'reviewText';
  text.maxLength = 2000;
  text.rows = 3;
  textLabel.append(text);
  const feedback = makeElement('p', 'text-sm text-red-200');
  feedback.setAttribute('role', 'alert');
  const submit = makeElement('button', 'bg-indigo-600 px-4 py-2 rounded', 'Submit review');
  submit.type = 'submit';

  form.append(heading, ratingLabel, rating, textLabel, feedback, submit);
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    submit.disabled = true;
    feedback.textContent = '';
    try {
      await requestJson('/api/reviews', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          movie_id: movieId,
          rating: Number(rating.value),
          text: text.value,
        }),
      });
      await openMovieDetails(movieId);
      await search();
    } catch (error) {
      feedback.textContent = `Could not submit review: ${error.message}`;
      submit.disabled = false;
    }
  });
  return form;
}

async function openMovieDetails(movieId) {
  detailsContent.replaceChildren(makeElement('p', '', 'Loading movie details…'));
  if (!detailsDialog.open) detailsDialog.showModal();
  try {
    const movie = await requestJson(`/api/movies/${movieId}`);
    detailsContent.replaceChildren();
    detailsContent.append(makeElement('h2', 'text-2xl font-bold', movie.title));
    detailsContent.append(
      makeElement(
        'p',
        'mt-1 text-sm text-indigo-200',
        `${movie.year ?? 'Year unknown'} · ⭐ ${movie.avg_rating.toFixed(1)} · ${movie.categories.map((category) => category.name).join(', ')}`,
      ),
    );
    detailsContent.append(makeElement('p', 'mt-4', movie.description || 'No description provided.'));
    detailsContent.append(makeElement('h3', 'mt-6 text-lg font-semibold', 'Reviews'));

    if (movie.reviews.length === 0) {
      detailsContent.append(makeElement('p', 'mt-2 text-indigo-200', 'No reviews yet.'));
    } else {
      const list = makeElement('ul', 'mt-2 space-y-3');
      movie.reviews.forEach((review) => {
        const item = makeElement('li', 'rounded bg-white/5 p-3');
        item.append(makeElement('p', 'text-yellow-300', `${review.rating} / 5 stars`));
        if (review.text) item.append(makeElement('p', 'mt-1', review.text));
        list.append(item);
      });
      detailsContent.append(list);
    }
    detailsContent.append(reviewForm(movie.id));
  } catch (error) {
    detailsContent.replaceChildren(makeElement('p', 'text-red-200', `Could not load movie details: ${error.message}`));
  }
}

btnSearch.addEventListener('click', () => search(true));
searchInput.addEventListener('input', () => {
  window.clearTimeout(searchTimer);
  searchTimer = window.setTimeout(() => search(true), 300);
});
searchInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    window.clearTimeout(searchTimer);
    search(true);
  }
});
categorySelect.addEventListener('change', () => search(true));
minRatingSelect.addEventListener('change', () => search(true));
yearSelect.addEventListener('change', () => search(true));
previousPageButton.addEventListener('click', () => {
  if (currentPage > 1) {
    currentPage -= 1;
    search();
  }
});
nextPageButton.addEventListener('click', () => {
  if (currentPage * pageSize < totalMovies) {
    currentPage += 1;
    search();
  }
});
closeDetailsButton.addEventListener('click', () => detailsDialog.close());
detailsDialog.addEventListener('click', (event) => {
  if (event.target === detailsDialog) detailsDialog.close();
});

window.addEventListener('load', async () => {
  try {
    await Promise.all([loadCategories(), loadYears(), loadRecommendations()]);
    await search();
  } catch (error) {
    setStatus(`Could not load the movie catalog: ${error.message}`);
  }
});
