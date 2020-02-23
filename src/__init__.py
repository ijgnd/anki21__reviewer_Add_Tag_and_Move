# License: GNU AGPL, version 3 or later; 

# original version for 2.0 at https://ankiweb.net/shared/info/1521848036
# published in 2015-08-05, copyright: unknown
# the original add-on says:
# "inspired by this article: 
#    http://moritzmolch.com/932
#    And by the addon Quick_Tagging by Cayenne Boyer Copyright 2012"
# also contains code from anki's aqt/browser.py which is Copyright: Damien Elmes

# use this at your own-risk


from aqt import mw
from aqt.reviewer import Reviewer
from anki.hooks import wrap
from aqt.utils import getTag, tooltip
from anki.utils import intTime, ids2str

from anki.hooks import addHook



def load_config(c):
    global config
    config = c
load_config(mw.addonManager.getConfig(__name__))
mw.addonManager.setConfigUpdatedAction(__name__,load_config) 


#adjusted from end of method setDeck from aqt/browser.py
def move_cards_to_different_deck(ids, did):
    mod = intTime()
    usn = mw.col.sched.col.usn()
    scids = ids2str(ids)
    mw.col.sched.remFromDyn(ids)
    mw.col.sched.col.db.execute("""
        update cards set usn=?, mod=?, did=? where id in """ + scids,
                        usn, mod, did)


def just_add_tags():
    note = mw.reviewer.card.note()
    tags = config.get("Just_add_tag__tags",0)
    if tags:
        note.addTag(tags)
        tooltip('Added tag "%s"' % tags)
        note.flush()
    else:
        tooltip('error in config')


def add_tags_and_move():
    note = mw.reviewer.card.note()
    tags = config.get("add_tags_and_change_deck__tags",0)
    if tags:
        note.addTag(tags)
        note.flush()
        mw.checkpoint(_("Change Deck"))
        did = mw.col.decks.id(config.get("add_tags_and_change_deck__newdeck",0))
        if did:
            move_cards_to_different_deck([mw.reviewer.card.id],did)
            tooltip('Added tag "%s" and moved' % tags)
        else:
            tooltip('invalid setting: deck does not exist')
    else:
        tooltip('error in config for "add_tags_and_change_deck__tags"')
    mw.reset()    


def just_change_Deck():
    note = mw.reviewer.card.note()
    mw.checkpoint(_("Change Deck"))
    deckname = config.get("just_change_deck__newdeck",0)
    if deckname:
        did = mw.col.decks.id(deckname)
        move_cards_to_different_deck([mw.reviewer.card.id],did)
        tooltip('Card moved to "%s"' % deckname)
        mw.reset()
    else:
        tooltip('error in config for "just_change_deck__newdeck"')


def show_tag_dialog():
    note = mw.reviewer.card.note()
    (tagString, r) = getTag(mw, mw.col, 'Choose a tag:')
    note.addTag(tagString)
    tooltip('Added tag "%s"' % tagString)
    note.flush()




def addShortcuts21(shortcuts):
    additions = (
        (config.get("Just_add_tag__hotkey","7"), just_add_tags),
        (config.get("","8"), add_tags_and_move),
        (config.get("just_change_deck__hotkey","9"), just_change_Deck),
        (config.get("Add_tags_dialog__hotkey","0"), show_tag_dialog),
    )
    shortcuts += additions
addHook("reviewStateShortcuts", addShortcuts21)
