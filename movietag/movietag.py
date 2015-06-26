import argparse
import mimetypes
import omdb
import os
import re
import subprocess
import tvdb_api

def main():
    parser = argparse.ArgumentParser(description='Automatically apply metadata to movie files')
    parser.add_argument('file', type=argparse.FileType('rb', 0))
    parser.add_argument('-m', dest='movie', type=str, help='Movie title to search for')
    parser.add_argument('-s', dest='series', type=str, help='TV series to search for')
    parser.add_argument('-gt', dest='guesstv', action='store_true', help='Infer series based on filename')

    args = parser.parse_args()

    if (args.movie):
        print('Searching for movie: "%s"...' % args.movie)
        return movie_main(args)

    if (args.guesstv):
        print('Guessing television episode based on filename...')
        return tv_main(args)

def apply_meta(args, meta):
    mimetype = mimetypes.guess_type(os.path.abspath(args.file.name))

    if mimetype[0] in [
            'video/x-m4v',
            'video/mp4'
            ] or os.path.splitext(args.file.name)[1] in ['.m4v', '.mp4']:
        return apply_m4v_meta(args.file, meta)
    else:
        print('Unsupported file type: %s' % mimetype[0])


def movie_main(args):
    matches = search_movies(args.movie)
    selection = choose_match(matches)

    if selection:
        info = get_full_movie_info(selection.imdb_id)

        for k,v in info.items():
            print('%s:\t%s' % (k,v))

        if choice('Apply?'):
            apply_meta(args, info);


def guess_tv_attributes(name):
    name_re = re.compile(r'(.*)[sS](\d*)[eE](\d*)\.')
    matches = name_re.match(name)

    if matches:
        matches = matches.groups()
        name = matches[0].strip().replace('-', ' ').replace('_', ' ')
        season = int(matches[1])
        episode = int(matches[2])
        return (name, season, episode)


def tv_main(args):
    t = tvdb_api.Tvdb()
    name, season, ep = guess_tv_attributes(os.path.basename(args.file.name))

    episode = t[name][season - 1][ep]

    meta = get_tv_meta(episode)

    if meta:
        for k,v in meta.items():
            print('%s:\t%s' % (k,v))

        if args.guesstv or choice('Apply?'):
            apply_meta(args, meta);


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

def get_tv_meta(episode):
    imdb = omdb.get(imdbid=episode['imdb_id'])

    meta = AttrDict(
        title  = episode['episodename'],
        actors = imdb['actors'],
        year   = imdb['year'],
        plot   = episode['overview'],
        genre  = imdb['genre'],
    )

    return meta


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

