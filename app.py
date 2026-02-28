"""
Flask blog application.

This app demonstrates a simple blog that loads posts from a JSON file
and renders them using Jinja templates.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from flask import Flask, abort, redirect, render_template, request, url_for

app = Flask(__name__)

POSTS_PATH = Path("posts.json")


def load_posts() -> list[dict[str, Any]]:
    """
    Load blog posts from the JSON file.

    Returns:
        A list of post dictionaries.
    """
    with POSTS_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_posts(posts: list[dict[str, Any]]) -> None:
    """
    Save blog posts to the JSON file.

    Args:
        posts: List of post dictionaries to write.
    """
    with POSTS_PATH.open("w", encoding="utf-8") as file:
        json.dump(posts, file, ensure_ascii=False, indent=2)


def next_post_id(posts: list[dict[str, Any]]) -> int:
    """
    Compute the next post id.

    Args:
        posts: Existing posts.

    Returns:
        An integer id that is 1 greater than the current max id.
    """
    if not posts:
        return 1
    return max(int(p.get("id", 0)) for p in posts) + 1


@app.route("/")
def index() -> str:
    """
    Render the homepage with a list of posts.

    Returns:
        Rendered HTML for the index page.
    """
    posts = load_posts()
    return render_template("index.html", posts=posts)


@app.route("/post/<int:post_id>")
def post_detail(post_id: int) -> str:
    """
    Render the detail page for a single post.

    Args:
        post_id: The numeric id of the post to display.

    Returns:
        Rendered HTML for the post detail page.

    Raises:
        404 error if the post does not exist.
    """
    posts = load_posts()
    post = next((p for p in posts if p.get("id") == post_id), None)

    if post is None:
        abort(404)

    return render_template("post.html", post=post)

@app.route("/delete/<int:post_id>")
def delete(post_id: int):
    """
    Delete a blog post by id and redirect to the homepage.

    Args:
        post_id: The numeric id of the post to delete.

    Returns:
        A redirect to the index page.
    """
    posts = load_posts()
    updated_posts = [p for p in posts if p.get("id") != post_id]
    save_posts(updated_posts)
    return redirect(url_for("index"))


@app.route("/add", methods=["GET", "POST"])
def add() -> str:
    """
    Display the add form (GET) and handle adding a new post (POST).

    Returns:
        Rendered HTML for GET, or a redirect response after POST.
    """
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        author = request.form.get("author", "").strip()

        if not title or not content:
            return render_template("add.html")

        posts = load_posts()
        post = {
            "id": next_post_id(posts),
            "title": title,
            "content": content,
            "author": author,
        }
        posts.append(post)
        save_posts(posts)

        return redirect(url_for("index"))

    return render_template("add.html")

@app.route("/update/<int:post_id>", methods=["GET", "POST"])
def update(post_id: int):
    """
    Update an existing blog post by id.

    GET: display a pre-filled update form.
    POST: save the updated post back to the JSON file.

    Args:
        post_id: The numeric id of the post to update.

    Returns:
        Rendered HTML for GET, or a redirect to the homepage after POST.
    """
    posts = load_posts()
    post = next((p for p in posts if p.get("id") == post_id), None)

    if post is None:
        abort(404)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        author = request.form.get("author", "").strip()

        if not title or not content:
            return render_template("update.html", post=post)

        post["title"] = title
        post["content"] = content
        post["author"] = author

        save_posts(posts)
        return redirect(url_for("index"))

    return render_template("update.html", post=post)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)