import time
import requests
from bs4 import BeautifulSoup
import math
from tqdm import tqdm
from termcolor import colored

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
}


def users_credentials():
    with open("credentials.txt", "r") as file:
        content = file.read().split()

    if content[0] == "NEW_USER":
        print("Welcome to Firefly's GitHub Unfollowers. \n"
              "Read the Readme.md file and understand the required credentials.")
        username_ = input("Enter your GitHub username: ")
        password_ = input("Enter your GitHub password: ")
        token_ = input(f"Enter your GitHub Unique Token.\n"
                       f"Read the Readme.md file to understand GitHub Unique Token and how to get it: ")

        with open("credentials.txt", "w") as file:
            file.write(f"EXISTING_USER {username_} {password_} {token_}")
    else:
        username_ = content[1]
        password_ = content[2]
        token_ = content[3]

    return username_, password_, token_


user_name = users_credentials()[0]
user_password = users_credentials()[1]
user_token = users_credentials()[2]


login_data = {
    'commit': 'Sign in',
    'utf8': '%E2%9C%93',
    'login': user_name,
    'password': user_password
}

# Create a session so that we remain logged in
url = 'https://github.com/session'
session = requests.Session()
response = session.get(url, headers=headers)

# Log in
soup = BeautifulSoup(response.text, 'lxml')
login_data['authenticity_token'] = soup.find('input', attrs={'name': 'authenticity_token'})['value']
response = session.post(url, data=login_data, headers=headers)

# Go to the followers page
response = session.get(f'https://github.com/{user_name}?tab=following', headers=headers).content
soup = BeautifulSoup(response, "lxml")

# Get the number of followers and unfollowers
followers_and_unfollowing_page = soup.find("div",class_ ="flex-order-1 flex-md-order-none mt-2 mt-md-0")
followers_and_following_numbers = followers_and_unfollowing_page.findAll("span", class_ ="text-bold color-fg-default")
followers = [i.text for i in followers_and_following_numbers][0]
following = [i.text for i in followers_and_following_numbers][1]

following_pages = math.ceil(int(following)/50)
followers_pages = math.ceil(int(followers)/50)
print(f"Followers: {followers}\nFollowing: {following}")



# Get all following usernames
print("Fetching Following...")
time.sleep(1)
following_usernames_list = []
for i in tqdm(range(following_pages)):
    response = session.get(f'https://github.com/{user_name}?page={i+1}&tab=following', headers=headers).content
    soup = BeautifulSoup(response, "lxml")

    usernames = soup.find("turbo-frame", id="user-profile-frame").findAll("span", class_="Link--secondary pl-1")
    usernames2 = soup.find("turbo-frame", id="user-profile-frame").findAll("span", class_="Link--secondary")

    following_usernames_list.extend([i.text for i in usernames2])
    following_usernames_list.extend([i.text for i in usernames])

following_usernames_list = list(dict.fromkeys(following_usernames_list))

# print(f"{following_usernames_list}\nLength: {len(following_usernames_list)}")

# Getting a list of all followers
print("Fetching followers...")
time.sleep(1)
followers_usernames_list = []
for i in tqdm(range(followers_pages)):
    response = session.get(f'https://github.com/{user_name}?page={i+1}&tab=followers', headers=headers).content
    soup = BeautifulSoup(response, "lxml")

    usernames = soup.find("turbo-frame", id="user-profile-frame").findAll("span", class_="Link--secondary pl-1")
    usernames2 = soup.find("turbo-frame", id="user-profile-frame").findAll("span", class_="Link--secondary")

    followers_usernames_list.extend([i.text for i in usernames2])
    followers_usernames_list.extend([i.text for i in usernames])


followers_usernames_list = list(dict.fromkeys(followers_usernames_list))


# A function to time the unfollowing to ensure a maximum of 100 followers an hour
def unfollow_timer(x):
    for minutes in range(x-1, -1, -1):
        for seconds in range(59, -1, -1):
            if seconds < 10 and minutes < 10:
                print(colored(f"\r0{minutes}:0{seconds}", "green"), end='', flush=True)
                time.sleep(0.5)
                print(colored(f"\r0{minutes} 0{seconds}", "green"), end='', flush=True)
                time.sleep(0.5)

            elif seconds < 10 and minutes > 9:
                print(colored(f"\r{minutes}:0{seconds}", "green"), end='', flush=True)
                time.sleep(0.5)
                print(colored(f"\r{minutes} 0{seconds}", "green"), end='', flush=True)
                time.sleep(0.5)

            elif seconds > 9 and minutes < 10:
                print(colored(f"\r0{minutes}:{seconds}", "green"), end='', flush=True)
                time.sleep(0.5)
                print(colored(f"\r0{minutes} {seconds}", "green"), end='', flush=True)
                time.sleep(0.5)

            else:
                print(colored(f"\r{minutes}:{seconds}", "green"), end='', flush=True)
                time.sleep(0.5)
                print(colored(f"\r{minutes} {seconds}", "green"), end='', flush=True)
                time.sleep(0.5)

    print(colored(f"\r00:00", "green"), end='', flush=True)


print("Identifying unfollowers...")
unfollowers = []
time.sleep(1)
for i in following_usernames_list:
    if i not in followers_usernames_list:
        unfollowers.append(i)

print(f"You have {len(unfollowers)} unfollowers")
time.sleep(2)

unfollowed_successfully = 0
unfollowed_unsuccessfully = 0
finished_unfollowing = False
print("Unfollowing users...\n")
while finished_unfollowing is False:
    for unfollow_username in unfollowers[:50]:
        try:
            headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"token {user_token}"
            }

            response = requests.delete(f'https://api.github.com/user/following/{unfollow_username}', headers=headers)
            if response.status_code == 204:
                unfollowed_successfully += 1
            else:
                unfollowed_unsuccessfully += 1

            print(colored(f"\rSuccessfully unfollowed {unfollow_username:20s}|| "
                          f"Total unfollowed: {unfollowed_successfully}", "green"), end='', flush=True)
            time.sleep(1)

        except:
            print("There was an error trying to unfollow your unfollowers!.\nThis may be due to an Invalid GitHub personal"
                  " access token. Generate a new token and restart this application.")
            finished_unfollowing = True
            break
    unfollowers = unfollowers[50:]

    if unfollowers == []:
        finished_unfollowing = True
        break

    print("\nTo follow the community guidelines, you have to wait for 30 minutes to unfollow the next 50 unfollowers. Please be patient")
    unfollow_timer(30)



print(f"\nUnfollowing complete!\n\n"
      f"Sucessfully unfollowed: {unfollowed_successfully}\n"
      f"Failed unfollowed     : {unfollowed_unsuccessfully}\n")

input("Thank you for using Firefly Corp Services. Press ank key to exit.")
