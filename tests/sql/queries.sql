-- name: SelectOne :one
SELECT * FROM sqlc_test WHERE name = $1;

-- name: SelectMany :many
SELECT * FROM sqlc_test;

-- name: InsertOne :exec
INSERT INTO sqlc_test(name, description) VALUES($1, $2);
