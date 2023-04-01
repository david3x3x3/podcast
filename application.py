import os
from sqlalchemy import create_engine, ForeignKey, Column, Integer
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, SelectField
from wtforms.validators import DataRequired

#app.config['MYSQL_HOST'] = os.environ.get('HOST')

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username = os.getenv('DB_USER'),
    password = os.getenv('DB_PASS'),
    hostname = os.getenv('DB_HOST'),
    databasename = os.getenv('DB_NAME')
)

engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, pool_recycle=3600)
Base = declarative_base()
Base.metadata.bind = engine
session = sessionmaker(engine)()

class audio(Base):
    __tablename__ = "audio"
    __table_args__ = {'autoload': True}

    event = Column(Integer, ForeignKey("audio_event.id"))
    audio_event = relationship('audio_event', foreign_keys=[event])

    speaker = Column(Integer, ForeignKey("audio_speaker.id"))
    audio_speaker = relationship('audio_speaker', foreign_keys=[speaker])

    series = Column(Integer, ForeignKey("audio_series.id"))
    audio_series = relationship('audio_series', foreign_keys=[series])

class audio_speaker(Base):
    __tablename__ = "audio_speaker"
    __table_args__ = {'autoload': True}

class audio_event(Base):
    __tablename__ = "audio_event"
    __table_args__ = {'autoload': True}

class audio_series(Base):
    __tablename__ = "audio_series"
    __table_args__ = {'autoload': True}

application = Flask(__name__)
application.config["DEBUG"] = True

application.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
application.config["SQLALCHEMY_POOL_RECYCLE"] = 299
application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
application.config['SECRET_KEY'] = os.getenv('WTF_SECRET')

#db = SQLAlchemy(app)

class SearchForm(FlaskForm):
    speaker = SelectField(u'Speaker:', choices = [], validate_choice=True)
    event = SelectField(u'Event:', choices = [], validate_choice=True)
    date_before = DateField(u'Delivered Before this Date:')
    date_after = DateField(u'Delivered After this Date:')
    passage = SelectField(u'Passage:', choices = [], validate_choice=True)
    series = SelectField(u'Series:', choices = [], validate_choice=True)

@application.route("/", methods=["GET", "POST"])
def search():
    form = SearchForm()

    if request.method == 'POST':
        a1 = session.query(audio)

        speaker_id = request.form['speaker']
        if speaker_id != '0':
            a1 = a1.where(audio.speaker == int(speaker_id))

        event_id = int(request.form['event'])
        if event_id != 0:
            a1 = a1.where(audio.event == event_id)

        series_id = int(request.form['series'])
        if series_id != 0:
            a1 = a1.where(audio.series == series_id)

        passage = request.form['passage'].strip()
        if passage != '':
            a1 = a1.where(audio.passage == passage)

        date_before = request.form['date_before']
        if date_before != '':
            a1 = a1.filter(audio.deliveryDate < date_before)

        date_after = request.form['date_after']
        if date_after != '':
            a1 = a1.filter(audio.deliveryDate > date_after)

        a1 = a1.order_by(audio.deliveryDate)

        return render_template('searchresults.html', aud=a1.all())

    choices = [('0','All')]
    for s1 in session.query(audio_speaker).all():
        choices += [(str(s1.id), s1.name)]
    choices.sort(key=lambda a: a[1])
    form.speaker.choices = choices

    choices = [('0','All')]
    for e1 in session.query(audio_event).all():
        choices += [(str(e1.id), e1.event)]
    form.event.choices = choices

    choices = [('','All')]
    for p1 in ('Genesis','Exodus','Leviticus','Numbers','Deuteronomy','Joshua','Judges',
        'Ruth','1 Samuel','2 Samuel','1 Kings','2 Kings','1 Chronicles','2 Chronicles',
        'Ezra','Nehemiah','Esther','Job','Psalm','Proverbs','Ecclesiastes','Song of Solomon',
        'Isaiah','Jeremiah','Lamentations','Ezekiel','Daniel','Hosea','Joel','Amos',
        'Obadiah','Jonah','Micah','Nahum','Habakkuk','Zephaniah','Haggai','Zechariah',
        'Malachi','Matthew','Mark','Luke','John','Acts','Romans','1 Corinthians',
        '2 Corinthians','Galatians','Ephesians','Philippians','Colossians','1 Thessalonians',
        '2 Thessalonians','1 Timothy','2 Timothy','Titus','Philemon','Hebrews','James',
        '1 Peter','2 Peter','1 John','2 John','3 John','Jude','Revelation'):
        choices += [(p1,p1)]
    form.passage.choices = choices

    choices = [(str(se1.id), se1.series) for se1 in session.query(audio_series).all()]
    choices.sort(key=lambda a: a[1])
    choices = [('0','All')] + choices
    form.series.choices = choices

    return render_template('search.html', form=form)

@application.route("/view")
def view():
    id = request.args.get('id')
    a1 = session.query(audio).where(audio.id == int(id)).first()
    return render_template('view.html', obj=a1)

class AudioForm(FlaskForm):
    id = IntegerField('name', validators=[DataRequired()])
    title = StringField('title', validators=[DataRequired()])
    deliveryDate = DateField('deliveryDate', validators=[DataRequired()])
    filePath = StringField('filePath', validators=[DataRequired()])
    passage = StringField('passage', validators=[DataRequired()])
    speaker = IntegerField('speaker', validators=[DataRequired()])
    event = IntegerField('event', validators=[DataRequired()])
    series = IntegerField('series', validators=[DataRequired()])
    reference = StringField('reference', validators=[DataRequired()])

@application.route("/audio", methods=["GET", "POST"])
def editaudio():
    a1 = session.query(audio).first()
    for col in audio.__table__.columns.keys():
        output += f'{col} = {str(getattr(a1,col))}\n'
    output += f'audio_speaker = {str(a1.audio_speaker.name)}\n'
    output += f'audio_event = {str(a1.audio_event.event)}\n'
    output += f'audio_series = {str(a1.audio_series.series)}\n'

    form = AudioForm(obj=None)
    return render_template('upload.html', form=form)

# main driver function
if __name__ == '__main__':
 
    # run() method of Flask class runs the application
    # on the local development server.
    application.run()
