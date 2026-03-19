from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def home():
    return render_template("home.html", page_title="Home")


@main_bp.get("/categories")
def categories():
    return render_template("categories.html", page_title="Categories")
