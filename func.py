from Morse_dictonery import morse_dic

# function to display on the screen
def display_in_morse_way(st: str):
    nstr = ""
    for i in st.lower():
        if i in morse_dic:
            for j in morse_dic[i]:
                nstr+=j
    return nstr


display_in_morse_way('hello')