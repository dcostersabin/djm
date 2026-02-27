-- +goose Up
-- +goose StatementBegin
--
-- Create model Example
--
CREATE TABLE "example" ("id" char(32) NOT NULL PRIMARY KEY, "name" varchar(100) NOT NULL);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
--
-- Create model Example
--
DROP TABLE "example";
-- +goose StatementEnd
