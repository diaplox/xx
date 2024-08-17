
import hashlib
import concurrent.futures
import argparse
import requests
from tqdm import tqdm

def md5_hash(word):
    return hashlib.md5(word.encode()).hexdigest()

def load_wordlist_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text.splitlines()

def generate_variations(word, num_range, symbols):
    variations = set()
    # Adding numbers to the word
    for i in range(num_range):
        variations.add(f"{word}{i}")
    
    # Adding special symbols
    for symbol in symbols:
        variations.add(f"{word}{symbol}")
    
    # Changing case
    variations.add(word.lower())
    variations.add(word.upper())
    variations.add(word.capitalize())
    
    return variations

def crack_md5_hash(hash_to_crack, words):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(md5_hash, word): word for word in words}
        for future in concurrent.futures.as_completed(futures):
            word = futures[future]
            try:
                if future.result() == hash_to_crack:
                    return word
            except Exception as exc:
                print(f"Word '{word}' raised an exception: {exc}")
    return None

def main():
    # Request MD5 input from the user
    md5_input = input("Please enter the MD5 hash you want to crack: ")
    
    parser = argparse.ArgumentParser(description="MD5 Hash Cracker")
    parser.add_argument("--wordlist-files", nargs='*', default=[], help="List of wordlist files")
    parser.add_argument("--wordlist-urls", nargs='*', default=[], help="List of wordlist URLs")
    parser.add_argument("--pass-list", type=str, help="Path to a custom password list file")
    parser.add_argument("--num-range", type=int, default=1000, help="Range of numbers to add to words")
    parser.add_argument("--symbols", nargs='*', default=['!', '@', '#', '$', '%', '^', '&', '*'], help="List of symbols to add to words")
    args = parser.parse_args()
    
    # Default wordlist, can be extended or replaced by custom pass list
    default_wordlist = [
        "password", "123456", "123456789", "qwerty", "abc123", "letmein", "welcome",
        "12345", "12345678", "1234567", "1234567890", "123123", "admin", "iloveyou",
        "letmein", "monkey", "dragon", "sunshine", "qwertyuiop", "123321", "password1",
        "1q2w3e4r", "111111", "abc123456", "password123", "1qaz2wsx", "qwerty123",
        "123qwe", "1q2w3e", "hello", "welcome123", "test123", "football", "baseball",
        "superman", "starwars", "trustno1", "batman", "qwerty1", "1234", "passw0rd",
        "monkey123", "123456a", "qwerty12345", "12345abc", "letmein123", "abc12345",
        "1qaz@wsx", "123abc", "password1234", "qwertyuiop123", "1qazxsw2", "123abc456",
        "myname", "123", "testpass", "1q2w3e4r5", "sunshine123", "hello12345"
    ]
    
    words = set(default_wordlist)

    # Load custom password list if provided
    if args.pass_list:
        try:
            with open(args.pass_list, 'r') as file:
                for line in file:
                    words.add(line.strip())
        except FileNotFoundError:
            print(f"Custom password list file not found: {args.pass_list}")

    # Load words from files if any are provided
    for wordlist_file in args.wordlist_files:
        try:
            with open(wordlist_file, 'r') as file:
                for line in file:
                    words.add(line.strip())
        except FileNotFoundError:
            print(f"File not found: {wordlist_file}")
    
    # Load words from URLs if any are provided
    for url in args.wordlist_urls:
        try:
            words.update(load_wordlist_from_url(url))
        except requests.RequestException as e:
            print(f"Error loading URL: {url}, {e}")
    
    print(f"Loaded {len(words)} words. Now starting to crack the hash...")

    # Generating variations of words
    all_variations = set()
    for word in tqdm(words, desc="Generating variations"):
        all_variations.update(generate_variations(word, args.num_range, args.symbols))
    
    cracked_word = crack_md5_hash(md5_input, all_variations)
    
    if cracked_word:
        print(f"Hash cracked! The original text is: {cracked_word}")
    else:
        print("No match found.")

if __name__ == "__main__":
    main()
