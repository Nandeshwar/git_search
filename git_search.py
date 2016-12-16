# Help:
# 1. Make sure python3 is installed in your system
# 2.
#   a. install modue requests using: pip3 install requests
#   b. install module validators: pip3 install validators
#
# 3. provide value for BASE_URL given below in code.
#    Don't worry about about user and password, you will be prompted for these
# 4. Run it like given below:
#python3 git_search.py "search=search_text"
#or
#python3 git_search.py "author=nandeshwa.sah:10"

import sys
import requests # pip3 install requests
import os
import datetime
from operator import itemgetter
import getpass
import validators

# Configuration portion
BASE_URL = "http://example1.com/"
BRANCHES = ["master", "develop", "development"]


class Git_Search:
    def __init__(self, user, password, base_url):
        self.user = user
        self.password = password
        if not base_url[len(base_url) -1] == "/":
            self.base_url = base_url + "/"
        else:
            self.base_url = base_url

        self.base_git_rest_url = self.base_url + "rest/api/1.0/"
        self.git_project_url = self.base_git_rest_url + "projects/"

    def convert_epoch_to_gmt(self, epoch_in_ms):
        return datetime.datetime.fromtimestamp(float(int(epoch_in_ms/1000))).strftime('%Y-%m-%d %H:%M:%S')

    def validate_url(self, url):
        if validators.url(url):
            return True
        else:
            return False

    def rest_call(self, url):
        try:
            if not self.validate_url(url):
                print("Not valid url=" + url)
                exit(0)
            print("Url="+ url)

            response = requests.get(url, auth=(self.user, self.password))

            # error message looks like given below
            # {'errors': [{'context': None, 'exceptionName': None, 'message': 'Authentication failed. Please check your credentials and try again.'}]}
            if "errors" in response.json().keys():
                for error in response.json()["errors"]:
                    if error["message"].find("Authentication failed") >= 0:
                        print(error)
                        exit(0)

            return response.json()
        except Exception as e:
            print(str(e))
            return {"errors":str(e), "url": url}

    def git_project_info(self):
        try:
            response = self.rest_call(self.git_project_url)
            return response
        except Exception as e:
            print(str(e))

    def all_project_names(self, project_info):
        project_names=[x["key"] for x in project_info["values"]]
        return project_names

    def project_repos(self, project_names):
        '''
         "data":[
                {
                    "project_name":"prj1",
                    "repos":[
                        {
                            "repo_name":"repo1"
                        }
                    ]
                }
            ]
        }

        '''
        project_repos = {
            "data":[
            ]
        }

        for project_name in project_names:
            repo_url = self.git_project_url + project_name + "/" + "repos?limit=100"
            response = self.rest_call(repo_url)

            repos = [{"repo_name": repo_info["slug"]} for repo_info in response["values"]]

            project_repos["data"].append({"project_name":project_name, "repos": repos})

        return project_repos

    def search_in_git(self, project_repo_info, search_data, author, commit_count):
        '''
        returns:
        "data":[
                  {
                      "repo_name="",
                      "author": "",
                      "url": BASE_URL + "projects/NKS/repos/nandeshwar/commits/63e348f7a84658910508b089426cbe9c37f2f434",
                      "message": "",
                      "date_epoch:123444,
                      "date_gmt:""
                  }
              ]
        }

        '''
        git_result = {
              "data":[
              ]
        }
        #TODO: Need to refactor this code
        for prj_info in project_repo_info["data"]:
            # if prj_info["project_name"] == "RMS":
                for repo in prj_info["repos"]:
                    # if(repo["repo_name"].lower() == "rmnxg"):
                        for branch in BRANCHES:
                            while True:
                                page = 1
                                limit = 1000
                                repo_committed_code_url=self.git_project_url + prj_info["project_name"] + "/repos/" + repo["repo_name"] + "/commits?until={branch}&start={start}&limit={limit}".\
                                    format(branch=branch, start=page, limit=limit)

                                response = self.rest_call(repo_committed_code_url)

                                if "errors" in response.keys():
                                    # Ignore error message if repo does not exist in branch(master, develop, development)
                                    if response["errors"][0]["message"].find("does not exist in repository") > -1:
                                        break
                                    print(response)
                                    break

                                stash_url = self.base_url + "projects/" + prj_info["project_name"] + "/repos/" + repo["repo_name"] + "/commits/"
                                search_result = self.find_message(response["values"], stash_url, author, search_data, commit_count, repo["repo_name"])

                                if len(search_result) > 0:
                                    git_result["data"].extend(search_result)

                                try:
                                    if response["isLastPage"] == "false":
                                        page = page + 1
                                    else:
                                        break
                                except Exception as e:
                                    print("Error while checking isLastePage" + str(e))
                                    break
        return git_result

    def find_message(self, committed_data, stash_url, author, message, commit_count, repo):
        search_result = []

        try:
            count = 0
            for res in committed_data:


                if res["message"].find("Merge pull request") < 0:
                    url = stash_url + res["id"]
                    searched_json= {
                        "author": res["author"]["name"],
                        "url": url, "message": res["message"],
                        "repo_name": repo,
                        "date_epoch": res["authorTimestamp"],
                        "date_gmt":self.convert_epoch_to_gmt(res["authorTimestamp"])
                    }

                    name_in_git = res["author"]["name"].lower()

                    if message:
                        search_data_arr = message.lower().split()

                        found_words = [search_word for search_word in search_data_arr
                                       if res["message"].lower().find(search_word) >= 0]
                        if len(found_words) == len(search_data_arr):
                            search_result.append(searched_json)
                    elif author:
                        author = author.lower()
                        first_last=author.split(".")

                        if (len(first_last) > 1 \
                                and name_in_git.find(first_last[0]) >= 0 \
                                and name_in_git.find(first_last[1]) >=0) \
                                or res["author"]["name"].lower().find(first_last[0]) >= 0:
                            count = count + 1
                            search_result.append(searched_json)
                            if count == commit_count:
                                count = 0
                                break


        except Exception as e:
            print("Error in method find_message="+str(e))
            raise Exception(str(e))

        return search_result

    def write_to_file(self, data, file, criteria):
        try:
            if criteria is None:
                with open(file, "w", newline="\r\n") as o:
                    for r in data["data"]:
                        author_info = "Author: " + r["author"]
                        stash_url = "Url: " + r["url"]
                        committed_message = "Message: " + r["message"]
                        date_gmt = "Date: " + r["date_gmt"]

                        o.write(author_info + '\n')
                        o.write(stash_url + '\n')
                        o.write(committed_message + '\n')
                        o.write(date_gmt)
                        o.write('\n\n')
            elif criteria == "by_author":
                sorted_data = sorted(data["data"], key=itemgetter('date_epoch'), reverse=True)
                all_repo_author_list = [(r["repo_name"], r["author"]) for r in data["data"]]
                all_repo = [x[0] for x in all_repo_author_list]
                author = [x[1] for x in all_repo_author_list]

                all_repo = set(all_repo)
                all_repo = list(all_repo)

                author = set(author)
                author_list = list(author)

                with open(file, "w", newline="\r\n") as o:
                    o.write("Commits found in the following projects\n")
                    o.write("Author:" + str(author_list) + "\n")

                    cnt = 0
                    for repo in all_repo:
                        cnt = cnt + 1
                        o.write(str(cnt) + "." + repo + "\n")
                    o.write("\n\n")

                    o.write("Top 20 latest commits\n")
                    o.write("\n")

                    cnt = 0
                    for top_committed_data in sorted_data:
                        cnt = cnt + 1
                        stash_url = "Url: " + top_committed_data["url"]
                        committed_message = "Message: " + top_committed_data["message"]
                        date_gmt = "Date: " + top_committed_data["date_gmt"]
                        o.write(str(cnt) + ".")
                        o.write(top_committed_data["repo_name"] + "\n")
                        o.write(stash_url+"\n")
                        o.write(committed_message+"\n")
                        o.write(date_gmt+"\n\n")
                        if cnt == 20:
                            break

                    o.write("\n")
                    o.write("\n")

                    for repo in all_repo:
                        o.write("\n----------Begin:" + repo + "----------\n\n")
                        for r in data["data"]:
                            if r["repo_name"].lower() == repo.lower():
                                author_info = "Author: " + r["author"]
                                stash_url = "Url: " + r["url"]
                                committed_message = "Message: " + r["message"]
                                date_gmt = "Date: " + r["date_gmt"]

                                o.write(author_info + '\n')
                                o.write(stash_url + '\n')
                                o.write(committed_message + '\n')
                                o.write(date_gmt + '\n')
                                o.write('\n')
                        o.write("----------End:" + repo + "----------\n")

            print("Search Result is saved to file {file}".format(file=os.path.abspath(file)))

        except Exception as e:
            print("Error writing to file {file}={error}".format(file=file, error=str(e)))

    @staticmethod
    def help_message():
        print('python3 git_search.py "search=search_text"')
        print("or")
        print('python3 git_search.py "author=nandeshwa.sah:10"')
        print("Note: author name can be just first name or last name or both of them combined with period(.)")
        print(":10 can be any number of >0. It is about number of commits to be fetched")




if __name__ == '__main__':
    arg_len = len(sys.argv)

    try:
        git_url_list = [
            "http://stash.example1.com/",
            "https://stash.example2.com/"
        ]

        print("BASE URL: " + BASE_URL)
        ans=input("Do want you change BASE URL n :Y/N: ")
        if ans.lower() == "y":
            print()
            for git_url in git_url_list:
                print(git_url)
            print()

            BASE_URL = input("Enter new BASE URL - Given above are few options: ")

        USER = input("GIT User Id: ")
        PASSWORD = getpass.getpass()

        git_search = Git_Search(USER, PASSWORD, BASE_URL)
        if arg_len < 2:
            git_search.help_message()
            exit(0)

        search_text = sys.argv[1]
        command, search_text = search_text.split("=")

        project_info = git_search.git_project_info()
        project_names = git_search.all_project_names(project_info)
        project_repo_info = git_search.project_repos(project_names)

        if command == "search":
            search_result = git_search.search_in_git(project_repo_info, search_text, None, None)
            search_file="search_{search_text}.txt".format(search_text=search_text)
            git_search.write_to_file(search_result, search_file, None)

        elif command == "author":
            try:
                author, commit_count=search_text.split(":")
                commit_count = int(commit_count)
                if commit_count <= 0:
                    git_search.help_message()
                    print("10 can be replaced with any number >0")

            except Exception as e:
                git_search.help_message()
                print("10 can be replaced with any number >0")
                exit(0)

            file_name = "search_{author}.txt".format(author=author)
            search_result = git_search.search_in_git(project_repo_info, None, author, commit_count)
            git_search.write_to_file(search_result, file_name, "by_author")

        else:
            print("Search criteria is wrong: It should be - search")
            print('python git_search.py "search=search_text"')
    except Exception as e:
        Git_Search.help_message()
        print(str(e))



