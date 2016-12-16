# git_search
Search in all the projects under git. 

# How to search
a. by author
--------------
python3 git_search.py "author=nandeshwar:10"


it will prompt:
BASE URL: http://example1.com/

Do want you change BASE URL n :Y/N:

enter y

it will prompt: 

http://stash.example1.com/

https://stash.example2.com/

Enter new BASE URL - Given above are few options:

enter new base url

Now it will prompt: 


GIT User Id:

Password:

enter user id and password and then proceed.

Note: it will search all the commits by given user in all the projects and list following things in a new file: 

a. All the repo name you have commited 

b. Top 20 commits and it's link

c. 10 commits per project and its link: 10 is parameter we have passed while running 


b. By text
-----------
python3 git_search.py "search_text=implemented daemo"

# Pre-steps

1. Make sure python3 is installed in your system

2.
 a. install modue requests using: pip3 install requests
 b. install module validators: pip3 install validators
 
3. provide value for BASE_URL given below in code.
  Don't worry about about user and password, you will be prompted for these
	
	4. Run it like given below:
  python3 git_search.py "search=search_text"
or
python3 git_search.py "author=nandeshwa.sah:10"
