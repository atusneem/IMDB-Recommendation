import urllib.request, urllib.parse, urllib.error
import json
import pymysql
import mysql.connector, time
from mysql.connector import Error
import pandas as pd
from rake_nltk import Rake
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import random


with open('APIkeys.json') as f:
    keys = json.load(f)
    omdbapi = keys['OMDBapi']

serviceurl = 'http://www.omdbapi.com/?'
apikey = '&apikey='+omdbapi

db = None
try:
    db = pymysql.connect(user='root', password='password', host='35.222.44.65', db='movies')
    cursor = db.cursor()
except:
    print('connection failed')

#createdb_query = "CREATE DATABASE IF NOT EXISTS movies"
#cursor.execute(createdb_query)
#db.commit()

cursor.execute("SET FOREIGN_KEY_CHECKS=0")
db.commit()

def createUser():
    print("Hello! Welcome to your new favorite movie recommendation app. To get started, please answer some of these questions.")
    first_input = input("Enter your first name: ")
    last_input = input("Enter your last name: ")
    genre = input("What is your favorite movie genre (please enter one)? ")

    customerid = (random.randrange(20, 50000, 3))
    insert_vals = (customerid, first_input, last_input, genre)

    add_user = "INSERT INTO customer(customer_id, first, last, genre) VALUES(%s, %s, %s, %s)"
    cursor.execute(add_user, insert_vals)
    db.commit()
    print("Your customer ID is: ", customerid, "use this to get access to your favorites and recommendations!")

    return customerid


def print_json(json_data):
    list_keys=['Title', 'Year', 'Rated', 'Released', 'Runtime', 'Genre', 'Director', 'Writer',
               'Actors', 'Plot', 'Language', 'Country', 'Awards', 'Ratings',
               'Metascore', 'imdbRating', 'imdbVotes', 'imdbID']
    print("-"*50)
    for k in list_keys:
        if k in list(json_data.keys()):
            print(f"{k}: {json_data[k]}")
    print("-"*50)


def save_in_database(json_data):
    customerID = input("What is your customerID?: ")
    title = json_data['Title']
    # Goes through the json dataset and extracts information if it is available
    if json_data['Year']!='N/A':
        year = int(json_data['Year'])
    if json_data['Runtime']!='N/A':
        runtime = int(json_data['Runtime'].split()[0])
    if json_data['Country']!='N/A':
        country = json_data['Country']
    if json_data['Metascore']!='N/A':
        metascore = float(json_data['Metascore'])
    else:
        metascore=-1
    if json_data['imdbRating']!='N/A':
        imdb_rating = float(json_data['imdbRating'])
    else:
        imdb_rating=-1

    # SQL commands
    cursor.execute("SELECT Title FROM MovieSearches WHERE Title = %s AND customerid = %s", (title,customerID,))
    row = cursor.fetchone()
    if row is None:
        insert_vals = (customerID, title, year, runtime, country, metascore, imdb_rating )
        userFavorites = """INSERT INTO MovieSearches (customerID, Title, Year, Runtime, Country, Metascore, IMDBRating)
                VALUES (%s,%s,%s,%s,%s,%s,%s)"""
        cursor.execute(userFavorites, insert_vals)
        print("Okay, it's saved!")
    else:
        print("You've saved this one already!")
    db.commit()


def save_recs(json_data):
    customerID = input("What is your customerID?: ")
    title = json_data['Title']
    # Goes through the json dataset and extracts information if it is available
    if json_data['Year']!='N/A':
        year = int(json_data['Year'])
    if json_data['Runtime']!='N/A':
        runtime = int(json_data['Runtime'].split()[0])
    if json_data['Country']!='N/A':
        country = json_data['Country']
    if json_data['Metascore']!='N/A':
        metascore = float(json_data['Metascore'])
    else:
        metascore=-1
    if json_data['imdbRating']!='N/A':
        imdb_rating = float(json_data['imdbRating'])
    else:
        imdb_rating=-1

    # SQL commands
    cursor.execute("SELECT Title FROM MovieRecs WHERE Title = %s AND customerid = %s", (title,customerID,))
    row = cursor.fetchone()
    if row is None:
        insert_vals = (customerID, title, year, runtime, country, metascore, imdb_rating )
        userFavorites = """INSERT INTO MovieRecs (customerID, Title, Year, Runtime, Country, Metascore, IMDBRating)
                VALUES (%s,%s,%s,%s,%s,%s,%s)"""
        cursor.execute(userFavorites, insert_vals)
        print("Okay, it's saved!")
    else:
        print("You've saved this one already!")
    db.commit()



def search_movie(title):
    if len(title) < 1 or title=='quit':
        print("Goodbye now...")
        return None
    try:
        url = serviceurl + urllib.parse.urlencode({'t': title})+apikey
        print(f'Retrieving the data of "{title}" now... ')
        uh = urllib.request.urlopen(url)
        data = uh.read()
        json_data=json.loads(data)
        if json_data['Response']=='True':
            print_json(json_data)
            save=input ('Would you like to save this movie to your favorites? Enter "yes" or "no": ').lower()
            if save=='yes':
                save_in_database(json_data)
        else:
            print("Error encountered: ",json_data['Error'])
    except urllib.error.URLError as e:
        print(f"ERROR: {e.reason}")

#reference from towards data science
def getData():
    df = pd.read_csv('https://query.data.world/s/uikepcpffyo2nhig52xxeevdialfl7')
    df = df[['Title','Genre','Director','Actors','Plot']]
    df['Actors'] = df['Actors'].map(lambda x: x.split(',')[:3])
    df['Genre'] = df['Genre'].map(lambda x: x.lower().split(','))
    df['Director'] = df['Director'].map(lambda x: x.split(' '))
    for index, row in df.iterrows():
        row['Actors'] = [x.lower().replace(' ', '') for x in row['Actors']]
        row['Director'] = ''.join(row['Director']).lower()

    df['Key_words'] = " "
    for index, row in df.iterrows():
        plot = row['Plot']
        r = Rake()
        r.extract_keywords_from_text(plot)
        key_words_dict_scores = r.get_word_degrees()
        row['Key_words'] = list(key_words_dict_scores.keys())
    # dropping the Plot column
    df.drop(columns = ['Plot'], inplace = True)
    df.set_index('Title', inplace = True)
    df['bag_of_words'] = ''
    columns = df.columns
    for index, row in df.iterrows():
        words = ''
        for col in columns:
            if col != 'Director':
                words = words + ' '.join(row[col])+ ' '
            else:
                words = words + row[col]+ ' '
        row['bag_of_words'] = words
    df.drop(columns = [col for col in df.columns if col!= 'bag_of_words'], inplace = True)
    count = CountVectorizer()
    count_matrix = count.fit_transform(df['bag_of_words'])
    indices = pd.Series(df.index)
    indices[:5]
    cosine_sim = cosine_similarity(count_matrix, count_matrix)
    cosine_sim

    #getting recommendations
    def recommendations(title, cosine_sim = cosine_sim):
        recommended_movies = []
        # gettin the index of the movie that matches the title
        idx = indices[indices == title].index[0]
        score_series = pd.Series(cosine_sim[idx]).sort_values(ascending = False)
        # getting the index of the 10 most similar movies
        top_10_indexes = list(score_series.iloc[1:11].index)
        for i in top_10_indexes:
            recommended_movies.append(list(df.index)[i])
        print(recommended_movies)
        return recommended_movies

    similarmovie = input("Which movie would you like to build your recommendations off of?: ")
    recommendations(similarmovie) #going through recommendation function
    save=input('Would you like to save this movie to your favorites? Enter "yes" or "no": ').lower()
    if save=='yes':
        #iterating through recommendations to save movies
        for i in recommendations(similarmovie):
            search_movie(i)
        print("Okay, it's saved!")
    else:
        "Okay, no problem!"

#View from past movie recommendations
def viewRec():
    customerID = input("Please enter your customerID: ")
    pastRecommendations = "SELECT * from pastRecommendations where customerID = %s"
    cursor.execute(pastRecommendations, customerID)
    result_set = cursor.fetchall()
    print("Past Recommendations: ")
    print(result_set)

#View from Movie Favorites table
def viewFaves():
    customerID = input("Please enter your customerID: ")
    favorites = "SELECT * from MovieFavorites where customerID = %s"
    cursor.execute(favorites, customerID)
    result_set = cursor.fetchall()
    print("Favorites: ")
    print(result_set)

#Start of program

print("Welcome to your new favorite movie recommendation app! Brought to you by IMDB.")
user_input = " "
while user_input != 5:
    print("1. Create a new account")
    print("2. Search for movies")
    print("3. Get a recommendation")
    print("4. View past recommendations")
    print("5. View favorite movies")
    print("6. Quit")
    user_input = input()

    if user_input == '1':
        createUser()
    elif user_input == '2':
        title = input('\nEnter the name of a movie to read info about it! (enter \'quit\' or hit ENTER to quit): ')
        if len(title) < 1 or title=='quit':
            print("Goodbye now...")
        else:
            search_movie(title)
    elif user_input == '3':
        getData()
    elif user_input == '4':
        viewRec()
    elif user_input == '5':
        viewFaves()
    else:
        print("Goodbye now!")
        break
