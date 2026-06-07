CREATE SCHEMA IF NOT EXISTS pantry;

-- users
CREATE TABLE pantry.users (
    id INT GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(50) NOT NULL,

    PRIMARY KEY (id)
);

-- ingredients
CREATE TABLE pantry.ingredients (
    id INT GENERATED ALWAYS AS IDENTITY,

    name VARCHAR(50) NOT NULL,
    category VARCHAR(30),

    PRIMARY KEY (id)
);

-- fridge_contents
CREATE TABLE pantry.fridge_contents (
    id INT GENERATED ALWAYS AS IDENTITY,

    ingredient_id INT NOT NULL,

    quantity NUMERIC(10,2) NOT NULL,
    unit VARCHAR(20),

    added_date DATE NOT NULL,
    expire_date DATE NOT NULL,

    PRIMARY KEY (id),

    FOREIGN KEY (ingredient_id)
    REFERENCES pantry.ingredients(id)
    ON DELETE CASCADE
);

-- recipes
CREATE TABLE pantry.recipes (
    id INT GENERATED ALWAYS AS IDENTITY,

    name VARCHAR(100) NOT NULL,
    description TEXT,

    PRIMARY KEY (id)
);

-- recipe_ingredients
CREATE TABLE pantry.recipe_ingredients (
    id INT GENERATED ALWAYS AS IDENTITY,

    recipe_id INT NOT NULL,
    ingredient_id INT NOT NULL,

    quantity NUMERIC(10,2),
    unit VARCHAR(20),

    PRIMARY KEY (id),

    FOREIGN KEY (recipe_id)
    REFERENCES pantry.recipes(id)
    ON DELETE CASCADE,

    FOREIGN KEY (ingredient_id)
    REFERENCES pantry.ingredients(id)
    ON DELETE CASCADE
);

--------------------------------------------------
-- users
--------------------------------------------------

INSERT INTO pantry.users(name)
VALUES
('Alice');

--------------------------------------------------
-- ingredients (20筆)
--------------------------------------------------

INSERT INTO pantry.ingredients(name, category)
VALUES
('雞蛋', '蛋類'),
('牛奶', '乳製品'),
('白飯', '主食'),
('蔥', '蔬菜'),
('雞胸肉', '肉類'),
('豬肉', '肉類'),
('高麗菜', '蔬菜'),
('紅蘿蔔', '蔬菜'),
('馬鈴薯', '蔬菜'),
('洋蔥', '蔬菜'),
('番茄', '蔬菜'),
('起司', '乳製品'),
('奶油', '乳製品'),
('吐司', '主食'),
('義大利麵', '主食'),
('鮪魚罐頭', '罐頭'),
('玉米', '蔬菜'),
('青椒', '蔬菜'),
('培根', '肉類'),
('蘑菇', '蔬菜');

--------------------------------------------------
-- recipes (5筆)
--------------------------------------------------

INSERT INTO pantry.recipes(name, description)
VALUES
('蛋炒飯', '使用雞蛋與白飯製作的家常料理'),
('奶油義大利麵', '使用奶油與義大利麵製作'),
('培根蛋吐司', '早餐常見料理'),
('番茄燉肉', '番茄與豬肉燉煮'),
('雞肉蔬菜湯', '雞胸肉與蔬菜熬煮');

--------------------------------------------------
-- recipe_ingredients
--------------------------------------------------

-- 蛋炒飯
INSERT INTO pantry.recipe_ingredients
(recipe_id, ingredient_id, quantity, unit)
VALUES
(1, 1, 2, '顆'),
(1, 3, 1, '碗'),
(1, 4, 1, '支');

-- 奶油義大利麵
INSERT INTO pantry.recipe_ingredients
(recipe_id, ingredient_id, quantity, unit)
VALUES
(2, 13, 20, '克'),
(2, 15, 1, '份'),
(2, 20, 3, '顆');

-- 培根蛋吐司
INSERT INTO pantry.recipe_ingredients
(recipe_id, ingredient_id, quantity, unit)
VALUES
(3, 19, 2, '片'),
(3, 1, 1, '顆'),
(3, 14, 2, '片');

-- 番茄燉肉
INSERT INTO pantry.recipe_ingredients
(recipe_id, ingredient_id, quantity, unit)
VALUES
(4, 6, 300, '克'),
(4, 11, 2, '顆'),
(4, 10, 1, '顆');

-- 雞肉蔬菜湯
INSERT INTO pantry.recipe_ingredients
(recipe_id, ingredient_id, quantity, unit)
VALUES
(5, 5, 300, '克'),
(5, 7, 200, '克'),
(5, 8, 100, '克');

--------------------------------------------------
-- fridge_contents (10筆)
--------------------------------------------------

INSERT INTO pantry.fridge_contents
(
    ingredient_id,
    quantity,
    unit,
    added_date,
    expire_date
)
VALUES
(1, 6, '顆', '2026-05-10', '2026-05-20'),
(2, 1, '瓶', '2026-05-11', '2026-05-18'),
(3, 2, '碗', '2026-05-11', '2026-05-13'),
(4, 3, '支', '2026-05-10', '2026-05-17'),
(5, 500, '克', '2026-05-09', '2026-05-16'),
(7, 1, '顆', '2026-05-08', '2026-05-14'),
(10, 2, '顆', '2026-05-11', '2026-05-19'),
(14, 1, '包', '2026-05-11', '2026-05-25'),
(19, 1, '包', '2026-05-10', '2026-05-15'),
(20, 8, '顆', '2026-05-11', '2026-05-18');

--------------------------------------------------
-- 測試查詢
--------------------------------------------------

-- 查看冰箱內容
SELECT
    fridge_contents.id,
    ingredients.name,
    fridge_contents.quantity,
    fridge_contents.unit,
    fridge_contents.expire_date
FROM pantry.fridge_contents
JOIN pantry.ingredients
ON fridge_contents.ingredient_id = ingredients.id;

-- 查看食譜需要材料
SELECT
    recipes.name AS recipe_name,
    ingredients.name AS ingredient_name,
    recipe_ingredients.quantity,
    recipe_ingredients.unit
FROM pantry.recipe_ingredients
JOIN pantry.recipes
ON recipe_ingredients.recipe_id = recipes.id
JOIN pantry.ingredients
ON recipe_ingredients.ingredient_id = ingredients.id;