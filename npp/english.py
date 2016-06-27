from gui import *
import pickle
from os.path import join
from startup import out, error

English_home = 'C:\\work_space\\home\\English'
#common_words is a set of known words
common_words_file = join(English_home, 'data', 'common_words.pckl')
def load_common_words():
    global common_words
    common_words = pickle.load(open(common_words_file, 'rb'))
    list_common_words()
# user_words is a dictionary {eng: heb}
def load_user_words():
    global user_words, user_words_file
    dict_file = tkFileDialog.askopenfile(
        mode='rb', initialdir = join(English_home, 'data'))
    if dict_file:
        user_words_file = dict_file
        user_words = pickle.load(dict_file)
        list_user_words()
    else: 
        tkMessageBox.showerror("User words", "Could not open the user word list")

def update_common_words(word_list):
    global common_words
    common_words = set(w.strip().lower() for w in word_list)
    store = tkMessageBox.askyesno("store", "Store the common words?")
    if store: pickle.dump(word_list, open(common_words_file, 'wb'))

def update_user_words(word_dict):
    global user_words
    user_words = dict(get())
    editor.clearAll()
    out(user_words)
    store = tkMessageBox.askyesno("store", "Store the user words?")
    if store: pickle.dump(words, open(user_words_file, 'wb'))
    
