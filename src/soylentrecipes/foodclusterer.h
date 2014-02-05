// TODO rm this if useless
//
/**
 * Performs a perhaps crappy clustering
 */ // TODO this is conceptually a function, not a class.. so perhaps it should be a function inside a module (aka cpp file)?
class FoodClusterer
{
public:
    void cluster(Foods& foods);

private:
    bool are_orthogonal(const FoodIt food1, const FoodIt food2);
};

bool FoodClusterer::are_orthogonal(const FoodIt food1, const FoodIt food2) {
    const double theta = 22.0 * (2.0 * M_PI / 360.0); // the minimum angle between 2 foods for them to be sufficiently different
    const double max_similarity = cos(theta);  // = cos theta, where theta is the minimum angle between 2 foods in a valid combination; 0.3 -> 72 degrees
    return food1->get_similarity(*food2) <= max_similarity;
}

void FoodClusterer::cluster(Foods& foods) {
    //forward_list<FoodIt> foods(foods.begin(), foods.end());
    map<FoodIt, vector<FoodIt>> food_groups;

    for (FoodIt food = foods.begin(); food != foods.end(); food++) {
        bool orthogonal = true;
        for (auto& item : food_groups) {
            if (!are_orthogonal(item.first, food)) {
                orthogonal = false;
                item.second.push_back(food);
                break;
            }
        }
        if (orthogonal) {
            cout << "!";
            food_groups.insert(make_pair(food, vector<FoodIt>()));
        }
        else {
            cout << ".";
        }
    }

    cout << endl;
    for (auto item : food_groups) {
        cout << item.first->get_id() << ": " << item.second.size() << endl;
        /*for (auto f : item.second) {
            cout << f->get_description() << endl;
        }*/
    }
    cout << "Orthogonal food count: " << food_groups.size() << endl;
}
