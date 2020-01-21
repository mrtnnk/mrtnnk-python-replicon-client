from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Numeric, select, func
from sqlalchemy.orm import sessionmaker
import yaml

DATABASE_ENV = 'mysql'
TABLE_NAME = 'RepliconCloud_INSERT'

with open('libs/database.yml', 'r') as f:
  config = yaml.safe_load(f)[DATABASE_ENV]
  DB_URL = '{}://{}:{}@{}:{}/{}'.format(
    config['adapter'],
    config['user'],
    config['password'] if config['password'] is not None else '',
    config['host'],
    config.get('port', '3306'),
    config['database']
  )

if config is not None:
  engine = create_engine(
    DB_URL
  )

Base = declarative_base()
_session = sessionmaker(bind=engine)
session = _session()

print("Create SQL table '{}'".format(TABLE_NAME))
class TimesheetBilling(Base):
  __tablename__ = TABLE_NAME
  BillingID = Column(Integer, primary_key=True)
  Entrydate = Column(DateTime)
  Staffingweek = Column(DateTime)
  Billhours = Column(Numeric(6, 2))
  HourlyRate = Column(Numeric(6, 2))
  Startdate = Column(DateTime)
  Enddate = Column(DateTime)
  Projectname = Column(String(255))
  Projectcode = Column(String(255))
  email = Column(String(255))
  Title = Column(String(255))
  TimesheetSlug = Column(String(255))
  ProjectSlug = Column(String(255))
  UserSlug = Column(String(255))

  @classmethod
  def length(self):
    return session.query(self).count()

  @classmethod
  def insert(self, data):
    session.add(data)
    session.commit()

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)