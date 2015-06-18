import os
import omdb
import argparse
import subprocess
import mimetypes

def main():
    parser = argparse.ArgumentParser(description='Automatically apply metadata to movie files')
    parser.add_argument('file', type=argparse.FileType('rb', 0))
    parser.add_argument('-m', dest='movie', type=str, help='Movie title to search for')

    args = parser.parse_args()

    if (args.movie):
        print('Searching for movie: "%s"...' % args.movie)
        return movie_main(args)


def movie_main(args):
    matches = search_movies(args.movie)
    selection = choose_match(matches)

    if selection:
        info = get_full_movie_info(selection.imdb_id)

        for k,v in info.items():
            print('%s:\t%s' % (k,v))

        if choice('Apply?'):
            mimetype = mimetypes.guess_type(os.path.abspath(args.file.name))

            if mimetype[0] in [
                    'video/x-m4v',
                    'video/mp4'
                    ]:
                return apply_m4v_meta(args.file, info)
            else:
                print('Unsupported file type: %s' % mimetype[0])


def choice(message, default='y'):
    choices = 'Y/n' if default.lower() in ('y', 'yes') else 'y/N'
    choice = input('%s (%s) ' % (message, choices))
    values = ('y', 'yes', '') if default == 'y' else ('y', 'yes')
    return choice.strip().lower() in values


def search_movies(title):
    return omdb.search_movie(title)


def choose_match(choices):
    for item in choices:
        if choice("%s (%s)? " % (item.title, item.year)):
            return item

def get_full_movie_info(imdbid):
    return omdb.get(imdbid=imdbid)


def apply_mkv_meta(dest, meta):

    """
    ARTIST: 'actors'
    DATE_RELEASE: 'year'
    GENRE: 'genre'
    SYNOPSIS: 'plot'
    DIRECTOR: 'director'
    TITLE: 'title'
    """

def apply_m4v_meta(dest, meta):
    command = ['AtomicParsley']
    params = [
            '--title', meta.title,
            '--artist', meta.actors,
            '--year', meta.year,
            '--description', meta.plot,
            '--genre', meta.genre,
            '--overWrite'
            ]

    filepath = os.path.abspath(dest.name)
    return subprocess.call(command + [filepath] + params)

