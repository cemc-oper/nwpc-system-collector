from sqlalchemy import create_engine, func
from sqlalchemy import Column, Integer, String, Text, Date, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://" + \
                          "windroc" + \
                          ":" + "shenyang" + \
                          "@" + "10.28.32.175" + \
                          ":" + "3306" + \
                          "/" + "smslog" + \
                          "?" + "charset=utf8"

engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
Model = declarative_base()


class User(Model):
    __tablename__ = "user"

    user_id = Column(Integer(), primary_key=True)
    user_name = Column(String(45))

    def __init__(self):
        pass

    def columns(self):
        return [c.name for c in self.__table__.columns]

    def to_dict(self):
        return dict([(c, getattr(self, c)) for c in self.columns()])


class Repo(Model):
    __tablename__ = "repo"

    repo_id = Column(Integer(), primary_key=True)
    user_id = Column(Integer)
    repo_name = Column(String(45))
    repo_location = Column(String(100))
    current_version_id = Column(Integer())

    def __init__(self):
        pass

    def columns(self):
        return [c.name for c in self.__table__.columns]

    def to_dict(self):
        return dict([(c, getattr(self, c)) for c in self.columns()])


class RepoVersion(Model):
    __tablename__ = 'repo_version'

    repo_version_id = Column(Integer, primary_key=True)
    repo_id = Column(Integer())
    version_id = Column(Integer())
    version_name = Column(String(45))
    version_location = Column(String(100))
    head_line = Column(Text())


class Record(Model):
    __tablename__ = "record_nwp_cma20n03"

    record_id = Column(Integer(), primary_key=True)
    repo_id = Column(Integer())
    version_id = Column(Integer())
    line_no = Column(Integer())
    record_type = Column(String(100))
    record_date = Column(Date())
    record_time = Column(Time())
    record_command = Column(String(100))
    record_fullname = Column(String(200))
    record_additional_information = Column(Text())
    record_string = Column(Text())

    def __init__(self):
        pass

    def __repr__(self):
        return "<Record(id={record_id}, string='{record_string}'".format(
            record_id=self.record_id,
            record_string=self.record_string.strip()
        )

    def columns(self):
        return [c.name for c in self.__table__.columns]

    def to_dict(self):
        return dict([(c,getattr(self, c)) for c in self.columns() ])


if __name__ == "__main__":
    session = Session()
    query = session.query(func.count(Record.record_id))
    print query.scalar()