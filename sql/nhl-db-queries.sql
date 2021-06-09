-- Python query
SELECT
    season, team, game, gp, wins, losses, ot_losses, points,
    point_percent, reg_wins, reg_ot_wins, so_wins, gf, ga, 
    gf_per_gp, ga_per_gp, pp_percent, pk_percent, pp_net_percent, 
    pk_net_percent, sf_per_gp, sa_per_gp, fo_win_percent
FROM games
WHERE season BETWEEN 2009 AND 2018
;

-- Checking ties
-- It looks like there are no ties
SELECT *
FROM games
WHERE season BETWEEN 2009 AND 2018
    AND ties IS NOT NULL
;

-- Checking  number of games per season
SELECT count(*) --2542
FROM games
WHERE season BETWEEN 2018 AND 2018
;

SELECT count(*) -- 1271
FROM games
WHERE season BETWEEN 2018 AND 2018
    AND wins != 0
;

SELECT count(*) -- 1271
FROM games
WHERE season BETWEEN 2018 AND 2018
    AND (losses != 0 OR ot_losses != 0)
;

