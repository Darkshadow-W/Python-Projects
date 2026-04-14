from flask import Flask, render_template, request

app = Flask(__name__)

DINO_DATA = [
    {
        "name": "Tyrannosaurus rex",
        "category": "Theropod",
        "diet": "Carnivore",
        "period": "Cretaceous",
        "legs": "2",
        "length_m": 12,
        "description": "A giant meat-eater with tiny arms and powerful jaws."
    },
    {
        "name": "Velociraptor",
        "category": "Theropod",
        "diet": "Carnivore",
        "period": "Cretaceous",
        "legs": "2",
        "length_m": 2,
        "description": "A fast, intelligent hunter known for its speed and agility."
    },
    {
        "name": "Triceratops",
        "category": "Ornithischian",
        "diet": "Herbivore",
        "period": "Cretaceous",
        "legs": "4",
        "length_m": 9,
        "description": "A horned dinosaur with a large frill and strong build."
    },
    {
        "name": "Brachiosaurus",
        "category": "Sauropod",
        "diet": "Herbivore",
        "period": "Jurassic",
        "legs": "4",
        "length_m": 26,
        "description": "A long-necked giant that grazed from tall trees."
    },
    {
        "name": "Stegosaurus",
        "category": "Ornithischian",
        "diet": "Herbivore",
        "period": "Jurassic",
        "legs": "4",
        "length_m": 9,
        "description": "A plated dinosaur with tail spikes for defense."
    },
    {
        "name": "Ankylosaurus",
        "category": "Ornithischian",
        "diet": "Herbivore",
        "period": "Cretaceous",
        "legs": "4",
        "length_m": 6,
        "description": "A heavily armored dinosaur with a clubbed tail."
    }
]

CATEGORIES = ["Theropod", "Sauropod", "Ornithischian"]
DIETS = ["Carnivore", "Herbivore", "Omnivore"]
PERIODS = ["Triassic", "Jurassic", "Cretaceous"]
LEGS = ["2", "4"]


def predict_dinosaur(features):
    best_score = -1
    best_dino = None

    for dino in DINO_DATA:
        score = 0
        score += 2 if dino["category"] == features["category"] else 0
        score += 2 if dino["diet"] == features["diet"] else 0
        score += 1 if dino["period"] == features["period"] else 0
        score += 1 if dino["legs"] == features["legs"] else 0

        input_length = features.get("length_m")
        if input_length is not None:
            score -= abs(dino["length_m"] - input_length) * 0.1

        if score > best_score:
            best_score = score
            best_dino = dino

    return best_dino


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        category = request.form.get("category")
        diet = request.form.get("diet")
        period = request.form.get("period")
        legs = request.form.get("legs")
        length_m = request.form.get("length_m")

        try:
            length_m = float(length_m) if length_m else None
        except ValueError:
            length_m = None

        features = {
            "category": category,
            "diet": diet,
            "period": period,
            "legs": legs,
            "length_m": length_m,
        }

        result = predict_dinosaur(features)

    return render_template(
        "index.html",
        categories=CATEGORIES,
        diets=DIETS,
        periods=PERIODS,
        legs_options=LEGS,
        result=result,
    )


if __name__ == "__main__":
    app.run(debug=True)
