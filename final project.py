import os 
import json
from pathlib import Path
from datetime import datetime
from typing import Dict,List,Optional,Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm

console= Console()

users: Dict[str, Dict]={}
posts: List[Dict]= []
stories: List[Dict]=[]
comments: List[Dict]= []
messages: List[Dict]= []
follow_requests: List[Dict]= []

DATA_DIR= "data"
USERS_FILE=os.path.join(DATA_DIR, "users.json")
POSTS_FILE=os.path.join(DATA_DIR, "posts.json")
STORIES_FILE=os.path.join(DATA_DIR, "stories.json")
COMMENTS_FILE=os.path.join(DATA_DIR, "comments.json")
MESSAGES_FILE=os.path.join(DATA_DIR, "messages.json")
FOLLOW_REQUESTS_FILE= os.path.join(DATA_DIR, "follow_requests.json")

def load_data():
    global users, posts, stories, comments, messages, follow_requests
    
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                users_data = json.load(f)
                users = {username: User.from_dict(data) for username, data in users_data.items()}
    except Exception as e:
        console.print(f"[red]error in loading users! {e}[/]")

    try:
        if os.path.exists(POSTS_FILE):
            with open(POSTS_FILE, "r", encoding="utf-8") as f:
                posts_data = json.load(f)
                posts = [Post.from_dict(data) for data in posts_data]
    except Exception as e:
        console.print(f"[red]error in uploading post {e}[/]")

def save_data():
    try:
        users_data = {username: user.to_dict() for username, user in users.items()}
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        console.print(f"[red]error in saving users {e}[/]")

    try:
        posts_data = [post.to_dict() for post in posts]
        with open(POSTS_FILE, "w", encoding="utf-8") as f:
            json.dump(posts_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        console.print(f"[red]error in saving posts {e}[/]")


#the main classes of our code
#each of users has these 
class User:
    def __init__(self, username:str, email: str, password:str):
        self.username= username
        self.email= email
        self.password= password
        self.bio= ""
        self.followers=[]
        self.following=[]
        self.posts=[]
        self.saved_posts=[]
        self.blocked_users=[]
        self.is_private = False  #by default baraye hame hesab ha ke public hastan
        self.created_at= datetime.now().isoformat()    
        
    def to_dict(self) -> Dict:
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "bio": self.bio,
            "followers": self.followers,
            "following": self.following,
            "posts": self.posts,
            "saved_posts": self.saved_posts,
            "blocked_users": self.blocked_users,
            "is_private": self.is_private,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        user = cls(data["username"], data["email"], data["password"])
        user.bio = data.get("bio", "")
        user.followers = data.get("followers", [])
        user.following = data.get("following", [])
        user.posts = data.get("posts", [])
        user.saved_posts = data.get("saved_posts", [])
        user.blocked_users = data.get("blocked_users", [])
        user.is_private = data.get("is_private", False)
        user.created_at = data.get("created_at", datetime.now().isoformat())
        return user
    
class Post:
    def __init__(self, author: str, caption: str, image_path: str = ""):
        self.id = len(posts) + 1
        self.author = author
        self.caption = caption
        self.image_path = image_path
        self.likes = []
        self.comments = []
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "author": self.author,
            "caption": self.caption,
            "image_path": self.image_path,
            "likes": self.likes,
            "comments": self.comments,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Post':
        post = cls(data["author"], data["caption"], data.get("image_path", ""))
        post.id = data["id"]
        post.likes = data.get("likes", [])
        post.comments = data.get("comments", [])
        post.created_at = data.get("created_at", datetime.now().isoformat())
        return post
    

def initialize_data_directory():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def register_user():

    console.print(Panel("register new user", style="blue"))
    
    while True:
        email = Prompt.ask("email")
        if "@" not in email or "." not in email:
            console.print("[red]wrong email format![/]")
            continue
        
        username = Prompt.ask("username")
        if username in users:
            console.print("[red]this username has been used before![/]")
            continue
        
        password = input("password: ")
        confirm_password = input("write password again: ")
        
        if password != confirm_password:
            console.print("[red]passwords don't match![/]")
            continue
        
        users[username] = User(username, email, password)
        save_data()
        console.print(f"[green]account {username} has been made successfully![/]")
        return username

def login_user() -> Optional[str]:

    console.print(Panel("login to account", style="blue"))
    
    username = Prompt.ask("username")
    if username not in users:
        console.print("[red]no username found![/]")
        return None
    
    password = input("password: ")
    if users[username].password != password:
        console.print("[red]wrong password[/]")
        return None
    
    console.print(f"[green]welcome back {username}![/]")
    return username


def home_screen(current_user: str):
    while True:
        console.print(Panel(f" HOME  welcome dear {current_user} !", style= "blue"))
        user = users[current_user]
        following_posts = [post for post in posts if post.author in user.following]
        
        if not following_posts:
            console.print("No posts")
        else:
            for post in following_posts:
                display_post(post, current_user)
        options= [
            ("1", "search for users"),
            ("2", "my profile"),
            ("3", "create new post"),
            ("4", "exit"),
        ]
        
        table = Table(show_header=False)
        table.add_column("choice", style="cyan")
        table.add_column("operations")

        for opt, desc in options:
            table.add_row(opt, desc)

        console.print(table)

        choice = Prompt.ask("choose an option", choices=["1", "2", "3", "4"])

        if choice == "1":
            search_users(current_user)
        elif choice == "2":
            profile_screen(current_user)
        elif choice == "3":
            create_post(current_user)
        elif choice == "4":
            return
        
        
def profile_screen(current_user: str):

    user = users[current_user]
    
    while True:
        console.print(Panel(f"*MY PROFILE* {current_user}", style="blue"))
        
        console.print(f"username: {current_user}")
        console.print(f"email: {user.email}")
        console.print(f"bio: {user.bio}")
        console.print(f"followers: {len(user.followers)}")
        console.print(f"followings: {len(user.following)}")
        console.print(f"posts: {len(user.posts)}")
        console.print(f"account's status: {'private' if user.is_private else 'public'}")
        
        options = [
            ("1", "edit profile"),
            ("2", "view my posts"),
            ("3", "saved post"),
            ("4", "privacy settings"),
            ("5", "blocked users"),
            ("6", "back")
        ]
        
        table = Table(show_header=False)
        table.add_column("option", style="cyan")
        table.add_column("operation")
        
        for opt, desc in options:
            table.add_row(opt, desc)
        
        console.print(table)
        
        choice = Prompt.ask("choose an option", choices=["1", "2", "3", "4", "5", "6"])
        
        if choice == "1":
            edit_profile(current_user)
        elif choice == "2":
            view_user_posts(current_user, current_user)
        elif choice == "3":
            view_saved_posts(current_user)
        elif choice == "4":
            privacy_settings(current_user)
        elif choice == "5":
            blocked_users(current_user)
        elif choice == "6":
            return
        
        
def display_post(post: Post, current_user: str):
    author = post.author
    caption = post.caption
    like_count = len(post.likes)
    comment_count = len(post.comments)
    created_at = datetime.fromisoformat(post.created_at).strftime("%Y-%m-%d %H:%M")
    
    panel = Panel(
        Text(f"{author} @ {created_at}\n\n{caption}\n\n❤ {like_count}   💬 {comment_count}"),
        title=f"#post{post.id}",
        border_style="green"
    )
    console.print(panel)
    
    if post.comments:
        console.print("💬 comments:")
        for comment_id in post.comments:
            comment = next((c for c in comments if c["id"] == comment_id), None)
            if comment:
                console.print(f"   {comment['author']}: {comment['text']}")
    options = [
        ("1", "like"),
        ("2", "comment"),
        ("3", "saved"),
        ("4", "back")
    ]
    
    table = Table(show_header=False)
    table.add_column("option", style="cyan")
    table.add_column("operation")
    
    for opt, desc in options:
        table.add_row(opt, desc)
    
    console.print(table)
    
    choice = Prompt.ask("choose one", choices=["1", "2", "3", "4"])
    
    if choice == "1":
        if current_user in post.likes:
            post.likes.remove(current_user)
            console.print("[yellow]you unliked![/]")
        else:
            post.likes.append(current_user)
            console.print("[green]you liked a post![/]")
        save_data()
    elif choice == "2":
        add_comment(post, current_user)
    elif choice == "3":
        if post.id not in users[current_user].saved_posts:
            users[current_user].saved_posts.append(post.id)
            console.print("[green]post has been saved![/]")
            save_data()
        else:
            console.print("[yellow]this post has already been saved before![/]")
    
def add_comment(post: Post, current_user: str):
    """adding comment to the post"""
    comment_text = Prompt.ask("write your comment ")
    comment_id = len(comments) + 1
    comments.append({
        "id": comment_id,
        "post_id": post.id,
        "author": current_user,
        "text": comment_text,
        "created_at": datetime.now().isoformat()
    })
    post.comments.append(comment_id)
    save_data()
    console.print("[green]your comment has been added![/]")
    
def view_profile(current_user: str, profile_user: str):
    user = users[profile_user]
    
    while True:
        console.print(Panel(f"{profile_user} profile", style="blue"))
        
        #user information
        console.print(f"user name: {profile_user}")
        console.print(f"bio: {user.bio}")
        console.print(f"followers number: {len(user.followers)}")
        console.print(f"following number: {len(user.following)}")
        console.print(f"posts number: {len(user.posts)}")
        
        options = []
        
        if profile_user != current_user:
            if profile_user in users[current_user].following:
                if profile_user in users[current_user].following:
                    
                    options.append(("1", "unfollow"))
            else:
                options.append(("1", "follow"))
            
            if profile_user in users[current_user].blocked_users:
                options.append(("2", "unblock"))
            else:
                options.append(("2", "block"))
        
        options.append(("3", "view posts"))
        options.append(("4", "back"))
        
        table = Table(show_header=False)
        table.add_column("option", style="cyan")
        table.add_column("operation")
        
        for opt, desc in options:
            table.add_row(opt, desc)
        
        console.print(table)
        
        choices = [opt for opt, _ in options]
        choice = Prompt.ask("choose", choices=choices)
        
        if choice == "1" and profile_user != current_user:
            if profile_user in users[current_user].following:
                users[current_user].following.remove(profile_user)
                user.followers.remove(current_user)
                console.print(f"[yellow]you're not following {profile_user} anymore![/]")
            else:
                if user.is_private:
                    
                    if any(req["from_user"] == current_user and req["to_user"] == profile_user for req in follow_requests):
                        console.print("[yellow]wait for your following request confirmation![/]")
                    else:
                        follow_requests.append({
                            "id": len(follow_requests) + 1,
                            "from_user": current_user,
                            "to_user": profile_user,
                            "status": "pending",
                            "created_at": datetime.now().isoformat()
                        })
                        console.print("[yellow]your request has been sent![/]")
                else:
                    users[current_user].following.append(profile_user)
                    user.followers.append(current_user)
                    console.print(f"[green]you are following {profile_user} now![/]")
            save_data()
        elif choice == "2" and profile_user != current_user:
            if profile_user in users[current_user].blocked_users:
                users[current_user].blocked_users.remove(profile_user)
                console.print(f"[green]user {profile_user} has been unblocked[/]")
            else:
                users[current_user].blocked_users.append(profile_user)
                
                #unfollow kardan
                if profile_user in users[current_user].following:
                    users[current_user].following.remove(profile_user)
                    user.followers.remove(current_user)
                console.print(f"[red]{profile_user} unfollowed![/]")
            save_data()
        elif choice == "3":
            view_user_posts(current_user, profile_user)
        elif choice == "4":
            return
        
        
def view_saved_posts(current_user: str):
    user = users[current_user]
    saved_posts = [post for post in posts if post.id in user.saved_posts]
    
    if not saved_posts:
        console.print("[yellow]no saved posts[/]")
        return
    
    console.print(Panel("Saved posts", style="blue"))
    
    for post in saved_posts:
        display_post(post, current_user)
        
def view_user_posts(current_user: str, profile_user: str):
    user = users[profile_user]
    user_posts = [post for post in posts if post.author == profile_user]
    
    if not user_posts:
        console.print("[yellow]no posts from this user![/]")
        return
    
    console.print(Panel(f"{profile_user}'s posts", style="blue"))
    
    for post in user_posts:
        display_post(post, current_user)
        
        
def search_users(current_user: str):
    console.print(Panel("search users", style="blue"))
    
    query = Prompt.ask("enter username (leave space to go back)")
    if not query:
        return
    
    results = [username for username in users if query.lower() in username.lower() and username != current_user]
    
    if not results:
        console.print("[yellow]no users were found![/]")
        return
    
    console.print("[cyan]search results:[/]")
    for i, username in enumerate(results, 1):
        user = users[username]
        console.print(f"{i}. {username} - followers: {len(user.followers)} - followings: {len(user.following)}")
    
    choice = Prompt.ask("to view profile enter number (0 to go back)", choices=[str(i) for i in range(len(results)+1)])
    if choice == "0":
        return
    
    selected_user = results[int(choice)-1]
    view_profile(current_user, selected_user)

        
        
def edit_profile(current_user: str):
    user = users[current_user]
    
    console.print(Panel("edit profile", style="blue"))
    
    new_bio = Prompt.ask("New bio (leave space for no changes)", default=user.bio)
    user.bio = new_bio
    
    save_data()
    console.print("[green]Profile has been updated sucessfully![/]")



def privacy_settings(current_user: str):
    user = users[current_user]
    
    console.print(Panel("privacy setting", style="blue"))
    
    user.is_private = Confirm.ask("are sure you want to change to private mode?", default=user.is_private)
    
    save_data()
    status = "private" if user.is_private else "public"
    console.print(f"[green]your account is {status} now![/]")
    
    
    
def create_post(current_user: str):
    console.print(Panel("create new post", style="blue"))
    
    caption = Prompt.ask("post's caption")
    #masir tasvir ra daryaft mikonim ama pardazesh nemikonim
    image_path = Prompt.ask("image path", default="")
    
    post = Post(current_user, caption, image_path)
    posts.append(post)
    users[current_user].posts.append(post.id)
    
    save_data()
    console.print("[green]post has been uploaded![/]")
    
def blocked_users(current_user: str):
    user = users[current_user]
    
    while True:
        console.print(Panel("blocked users", style="blue"))
        
        if not user.blocked_users:
            console.print("[yellow]you blocked no one![/]")
        else:
            for i, username in enumerate(user.blocked_users, 1):
                console.print(f"{i}. {username}")
        
        options = [
            ("1", "unblock"),
            ("2", "back")
        ]
        
        table = Table(show_header=False)
        table.add_column("option", style="cyan")
        table.add_column("operation")
        
        for opt, desc in options:
            table.add_row(opt, desc)
        
        console.print(table)
        
        choice = Prompt.ask("choose", choices=["1", "2"])
        
        if choice == "1" and user.blocked_users:
            selected = Prompt.ask("enter user number to unblock (enter 0 to go back)", 
                                choices=[str(i) for i in range(len(user.blocked_users)+1)])
            if selected == "0":
                continue
            
            unblocked_user = user.blocked_users[int(selected)-1]
            user.blocked_users.remove(unblocked_user)
            save_data()
            console.print(f"[green]{unblocked_user} unblocked![/]")
            
        elif choice == "2":
            return


def main():
    initialize_data_directory()
    load_data()
    console.print(Panel("instagram", style= "bold blue"))
    while True:
        options = [
            ("1", "Login"),
            ("2","register"),
            ("3", "Exit"),
        ]
        table= Table(show_header= False)
        table.add_column("choise", style="cyan")
        table.add_column("operations")
        
        for opt, desc in options:
            table.add_row(opt, desc)
            
        console.print(table)
        
        choice = Prompt.ask("choose an option", choices=["1", "2", "3"])
        
        if choice == "1":
            username = login_user()
            if username:
                home_screen(username)
        elif choice== "2":
            username = register_user()
            if username:
                home_screen(username)
        elif choice == "3":
            console.print("[green]Goodbye![/]")
            break
    
if __name__ == "__main__":
    main()        