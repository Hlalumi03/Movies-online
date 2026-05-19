from app.database import engine, Base, SessionLocal
from app import models, crud, schemas

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# create categories
cats = ['Action','Drama','Comedy','Sci-Fi','Romance']
for c in cats:
    if not db.query(models.Category).filter(models.Category.name==c).first():
        db.add(models.Category(name=c))

# create sample movies
if not db.query(models.Movie).filter(models.Movie.title=='Edge of Tomorrow').first():
    m = models.Movie(title='Edge of Tomorrow', year=2014, description='A soldier relives the same day.', avg_rating=4.2)
    m.categories.append(db.query(models.Category).filter(models.Category.name=='Action').one())
    m.categories.append(db.query(models.Category).filter(models.Category.name=='Sci-Fi').one())
    db.add(m)

if not db.query(models.Movie).filter(models.Movie.title=='Romantic Nights').first():
    m2 = models.Movie(title='Romantic Nights', year=2019, description='A modern love story.', avg_rating=3.8)
    m2.categories.append(db.query(models.Category).filter(models.Category.name=='Romance').one())
    db.add(m2)

if not db.query(models.Movie).filter(models.Movie.title=='Laugh Riot').first():
    m3 = models.Movie(title='Laugh Riot', year=2021, description='A standup comedy special.', avg_rating=4.5)
    m3.categories.append(db.query(models.Category).filter(models.Category.name=='Comedy').one())
    db.add(m3)


db.commit()
print('Seed complete')
