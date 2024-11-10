import sys
sys.path.insert(0, '.')
from swap import update_single_user_flair, get_swap_count, create_reddit_and_sub, update_flair
import requests
import argparse
import praw
import time
import datetime
sys.path.insert(0, 'tools')
import backfill

parser = argparse.ArgumentParser()
parser.add_argument('sub_name', metavar='C', type=str)
args = parser.parse_args()

platform = 'reddit'

sub_config, reddit, sub = create_reddit_and_sub(args.sub_name.lower())

request_url = "http://0.0.0.0:8000"
db = requests.get(request_url+"/get-sub-db/", data={'sub': sub_config.subreddit_name}).json()

if platform not in db:
	db[platform] = {}

unassigned_users = []
keys = list(db[platform].keys())
#keys = list(backfill.GetUsersFromCss(sub_config.subreddit_object).keys())
mods = [str(x).lower() for x in sub.moderator()]
#keys = mods
#keys = ['thedaddyog', '420artist', 'adtasty2000', 'ok_technology_9488', 'fabulous_mewtwo', 'therealveee', 'usernameannonomous', 'icy_protection_861', 'unwilt', 'mysteriousheart3827', 'humorwilling7370', 'justindigo88', 'polishedtangerine', 'pamisthicc', 'clerby89', 'turbulent_space_2733', 'impossibleday1782', 'sanskari_as_hell', 'greedy-ice1272', 'bean_lordjy', 'neitheranteater9140', 'embarrassed-bison362', 'jigglypuff6666', 'seerocka2000', 'odd_chip_5233', 'longjumping_sir3569', 'no-hotel-636', 'ron-my-white-name', 'istealeyeballs', 'best-goat-3618', 'educational-law3443', '200000alex', 'terrible_phone_4274', 'nobunnythere', 'bikerbob101', 'appropriate-bike9884', 'mangolechonk', 'local_h_jay', 'earthlymg', 'salty-love-5396', 'some_dumb_stuff69', 'brigham_youngblood', 'sadboy_b', '56rock6565', 'rosecoloredglasses-', 'im_just_a_artist', 'adept-sale2654', 'munchmyarm', 'character_rooster448', 'potatoes_6945', 'lost-fly6204', 'urielalan', '_okeythen_', 'aokahken', 'latronious', 'some-ostrich-4997', 'broclee8008135', 'speckledspoon2108', 'beccaacook', 'castleofwamdue', 'qayjay13', 'the_dnd_2', 'zootedmiraidon', 'adept-homework-292', '_marco_21', 'fearless_break_9260', 'justablaze333', 'absnail177', 'disposableboi69', 'excellent-warning802', 'humble-cauliflower50', 'plasmaofmystic', 'fuckyour_parlay', 'accomplished_sky215', 'iphd08', 'sist3n', 'significant_war_5924', 'ihaveskillissues', 'throwaway63608', 'nettop614', 'vacationmodesarah', 'pierdole-nie-robie', 'netcharming8593', 'dystopiannnn', 'cam200212', 'mediocre-nerve4286', 'f0x61', 'sncereno', 'ok-moment-8349', 'a_moron_in-existence', 'jumpy-tradition-8930', 'kiingluii', 'majestic-athlete-937', 'darkthunder9782', 'xaylorscats', 'atom0715', 'huntervill', 'few_quote9451', 'snowrises007', 'aa1512', 'normal_shopping3170', 'joshomama', 'nomainoonoparty', 'pulsecole', 'conebasher', 'sellsmart9072', 'educational-can-3867', 'accomplished-rip9149', 'motor_tadpole_6626', 'no-designer-6156', 'embarrassed-yard-272', 'novathegoober', 'amsyar_kailou', 'ghost183762', 'zavubabu8', 'striking-bumblebee35', 'fillmoslim', 'diglettfacts', 'sasukeuchiha99904', 'tanner_robart', 'interactionsea2986', 'darklordtrainer', 'thunderousrotom', 'maddiebaby56', 'internallopsided4535', 'tmill432', 'public-resolve-5408', 'jotarokujo7633', 'questingkingfisher', 'spongewhom', 'sacrimusprime', 'resident-kitchen-433', 'northenlights26', 'informal-love-7962', 'ooosiedooosie', 'kekemimichi', '-gflow-', 'pogo_datskwerrel', 'smashsquatchh', 'ambitiousstatus5689', 'filimignon', 'cold-pop-2893', 'kyano-c', 'thrawnschimera', 'upset-ad-3899', 'parking-dare49100', 'positive_tax3946', 'god_arceus_', 'dark_mage_69', 'enthuzstmikey']
keys = ['marmarjo']
keys.sort()


print("Running over " + str(len(keys)) + " users.")
for i in range(len(keys)):
	user = keys[i].lower()
	if user not in db[platform]:
		db[platform][user] = []
	count = str(get_swap_count(user, [sub_config.subreddit_name] + sub_config.gets_flair_from, platform))
	try:
		print(str(i) + ") Updating user " + user)
	except Exception as e:
		print(e)
		continue
	try:
		redditor = reddit.redditor(user)
		age = datetime.timedelta(seconds=(time.time() - redditor.created_utc)).days
#		update_flair(redditor, None, sub_config)
		flair = update_single_user_flair(sub, sub_config, str(redditor), count, unassigned_users, age)
		time.sleep(0.5)
	except:
		time.sleep(20)
		try:
			redditor = reddit.redditor(user)
			age = datetime.timedelta(seconds=(time.time() - redditor.created_utc)).days
#			update_flair(redditor, None, sub_config)
			flair = update_single_user_flair(sub, sub_config, str(redditor), count, unassigned_users, age, mods=mods)
			print(flair)
			time.sleep(0.5)
		except Exception as e:
			print("    Unable to update flair for " + user + " with error " + str(e))
			unassigned_users.append(user)


if unassigned_users:
	print("The following users did not get their flair updated:\n  " + "\n  ".join(unassigned_users))

