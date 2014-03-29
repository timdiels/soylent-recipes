#include <soylentrecipes/mining/RecipeProblem.h>
#include <cmath>
#include <iostream>
#include <assert.h>

using namespace std;
using namespace alglib;

void testRecipeProblem() {
    real_1d_array targets;
    targets.setlength(4);
    targets[0] = 300;
    targets[1] = 300;
    targets[2] = 300;
    targets[3] = 10;

    real_1d_array maxima;
    maxima.setlength(4);
    maxima[0] = 300;
    maxima[1] = INFINITY;
    maxima[2] = INFINITY;
    maxima[3] = INFINITY;

    NutrientProfile profile(targets, maxima);

    real_1d_array x;
    x.setlength(4);
    x[0] = 3;
    x[1] = 2;
    x[2] = 1;
    x[3] = 0;

    Food food1(1, "food1", x);

    x[0] = 0;
    x[1] = 2;
    x[2] = 4;
    x[3] = 0;
    Food food2(2, "food2", x);

    vector<Food*> foods;
    foods.push_back(&food1);
    foods.push_back(&food2);

    RecipeProblem problem(profile, foods.begin(), foods.end());
    problem.solve();
    auto result = problem.get_result();

    // solution: 100 * food1, 50 * food2
    assert(result.length() == 2);
    assert(result[0] == 100);
    assert(result[1] == 50);
    assert(problem.get_completeness() == 0.75);
}
