#! /usr/bin/env python3

import parse_iheart_json
import argparse
import subprocess

def launch_mplayer (url, mplayer_args):
	# Make sure we actually have mplayer
	try:
		subprocess.check_call (['which', 'mplayer'], shell=False)
	except subprocess.CalledProcessError:
		raise RuntimeError ('MPlayer could not be found.')

	# Now we run mplayer. Pass it '-novideo', since we're playing radio
	# streams which are obviously audio-only - otherwise some versions of
	# mplayer will spend minutes looking for a nonexistent video stream.
	subprocess.call (['mplayer', url, '-novideo'] + mplayer_args, shell=False)

def launch_vlc (url, vlc_args):
	# Make sure we actually have vlc
	try:
		subprocess.check_call (['which', 'vlc'], shell=False)
	except subprocess.CalledProcessError:
		raise RuntimeError ('VLC could not be found.')

	# Now we run vlc.
	subprocess.call (['vlc', url] + vlc_args, shell=False)

def dump_station_details (station):
	print ("station name:", station['name'])
	print ("call letters:", station['callLetters'])
	print ("location:", station['city'], station['state'], station['countries'])
	print ("description:", station['description'])
	print ("broadcast format:", station['format'])

	print ("available stream types:", end = ' ')
	for st in station['streams']:
		print (st, end = ' ')
	print ()

def play_station (station_id):
	station = parse_iheart_json.station_info (station_id)
	if (args.verbose):
		try:
			dump_station_details (station)
			if (args.verbose >= 3):
				print ("full dictionary dump:")
				print (station)
		except KeyError:
			print ("warning: a field is missing")
			# at >2 we've done this already
			if (verbose == 2):
				print ("full dictionary dump:")
				print (station)

	try:
		station_url = parse_iheart_json.get_station_url (station)
	except KeyError:
		print ("error: requested stream does not exist for this station")
		# at >2 we've done this already
		if (args.verbose == 2):
			print ("full dictionary dump:")
			print (station)
		exit ()

	if (args.player == 'mplayer'):
		launch_mplayer (station_url, (args.player_options[0].split() if args.player_options else []))
	elif (args.player == 'vlc'):
		launch_vlc (station_url, (args.player_options[0].split() if args.player_options else []))

if (__name__ == '__main__'):

	parser = argparse.ArgumentParser (description="Play an iHeartRadio station in mplayer or VLC")

	# Optional arguments
	parser.add_argument (
		'-p', '--player',
		default='mplayer',
		choices=['mplayer', 'vlc'],
		help="The player to use (currently either mplayer or vlc), the default is mplayer",
		)
	parser.add_argument (
		'-o', '--player-options',
		nargs=1,
		help="Command-line arguments to pass the media player, should be a quoted string beginning with a space. Yes, this is ugly, blame argparse.",
		)
	parser.add_argument (
		'-v', '--verbose',
		action='count',
		help="Display extra information",
		)
	parser.add_argument (
		'-i', '--info',
		action='store_true',
		help="Instead of playing station_id, output some information about it",
		)

	# The three required arguments; one and only one must be given

	action = parser.add_mutually_exclusive_group(required=True)
	action.add_argument (
		'station_id',
		nargs='?',
		type=int,
		help="The (five-digit?) ID number of the station",
		)
	action.add_argument (
		'-s', '--search',
		metavar='TERMS',
		help="List station search results for TERMS"
		)
	action.add_argument (
		'-l', '--lucky',
		metavar='TERMS',
		help="\"I\'m feeling lucky\" search for TERMS (play the first result)"
		)

	args = parser.parse_args ()

	if (args.search):
		results = parse_iheart_json.station_search (args.search)

		print ("hits:", results['totalStations'])
		for station in results['stations']:
			if (args.verbose):
				print ("\n-- name:", station['name'], "id:" + str(station['id']))
				print ('\t', "callsign:", station['callLetters'])
				print ('\t', "frequency:", station['frequency'])
				print ('\t', "city:", station['city'])
				print ('\t', "state:", station['state'])
				print ('\t', "description:", station['description'])
				print ('\t', "relevancy score:", station['score'])
			else:
				print (station['name'], '\t', station['description'], "id:" + str(station['id']))
	elif (args.lucky):
		results = parse_iheart_json.station_search (args.lucky)
		play_station (results['bestMatch']['id'])
	else:
		if (args.info):
			dump_station_details (parse_iheart_json.station_info (args.station_id))
		else:
			play_station (args.station_id)
