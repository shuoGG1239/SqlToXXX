package parser

import (
	"testing"
)

func TestParserCreateTableSimple(t *testing.T) {
	query := `CREATE TABLE account (id INT, email TEXT)`
	parse(query, 1, t)
}

func TestParserCreateTableSimpleWithPrimaryKey(t *testing.T) {
	query := `CREATE TABLE account (id INT PRIMARY KEY, email TEXT)`
	parse(query, 1, t)
}

func TestParserMultipleInstructions(t *testing.T) {
	query := `CREATE TABLE account (id INT, email TEXT);CREATE TABLE user (id INT, email TEXT)`
	parse(query, 2, t)
}

func TestParserComplete(t *testing.T) {
	query := `CREATE TABLE user
	(
    	id INT PRIMARY KEY,
	    last_name TEXT,
	    first_name TEXT,
	    email TEXT,
	    birth_date DATE,
	    country TEXT,
	    town TEXT,
	    zip_code TEXT
	)`
	parse(query, 1, t)
}

func TestParserCompleteWithBacktickQuotes(t *testing.T) {
	query := `CREATE TABLE ` + "`" + `user` + "`" + `
	(
		` + "`" + `id` + "`" + ` INT PRIMARY KEY,
		` + "`" + `last_name` + "`" + ` TEXT,
		` + "`" + `first_name` + "`" + ` TEXT,
		` + "`" + `email` + "`" + ` TEXT,
		` + "`" + `birth_date` + "`" + ` DATE,
		` + "`" + `country` + "`" + ` TEXT,
		` + "`" + `town` + "`" + ` TEXT,
		` + "`" + `zip_code` + "`" + ` TEXT
	)`
	parse(query, 1, t)
}

func TestCreateTableWithKeywordName(t *testing.T) {
	query := `CREATE TABLE test ("id" bigserial not null primary key, "name" text, "key" text)`
	parse(query, 1, t)
}

func TestCreateDefault(t *testing.T) {
	query := `CREATE TABLE foo (bar BIGINT, riri TEXT, fifi BOOLEAN NOT NULL DEFAULT false)`

	parse(query, 1, t)
}

func TestCreateDefaultNumerical(t *testing.T) {
	query := `CREATE TABLE foo (bar BIGINT, riri TEXT, fifi BIGINT NOT NULL DEFAULT 0)`

	parse(query, 1, t)
}

func TestCreateWithTimestamp(t *testing.T) {
	query := `CREATE TABLE IF NOT EXISTS "pokemon" (id BIGSERIAL PRIMARY KEY, name TEXT, type TEXT, seen TIMESTAMP WITH TIME ZONE)`

	parse(query, 1, t)
}

func TestCreateDefaultTimestamp(t *testing.T) {
	query := `CREATE TABLE IF NOT EXISTS "pokemon" (id BIGSERIAL PRIMARY KEY, name TEXT, type TEXT, seen TIMESTAMP WITH TIME ZONE DEFAULT LOCALTIMESTAMP)`

	parse(query, 1, t)
}

func TestCreateNumberInNames(t *testing.T) {
	query := `CREATE TABLE IF NOT EXISTS "pokemon" (id BIGSERIAL PRIMARY KEY, name TEXT, type TEXT, md5sum TEXT)`

	parse(query, 1, t)
}

func TestOffset(t *testing.T) {
	query := `SELECT * FROM mytable LIMIT 1 OFFSET 0`

	parse(query, 1, t)
}

func TestUnique(t *testing.T) {
	queries := []string{
		`CREATE TABLE pokemon (id BIGSERIAL, name TEXT UNIQUE NOT NULL)`,
		`CREATE TABLE pokemon (id BIGSERIAL, name TEXT NOT NULL UNIQUE)`,
		`CREATE TABLE pokemon_name (id BIGINT, name VARCHAR(255) PRIMARY KEY NOT NULL UNIQUE)`,
	}

	for _, q := range queries {
		parse(q, 1, t)
	}
}

func parse(query string, instructionNumber int, t *testing.T) []Instruction {
	parser := parser{}
	lexer := lexer{}
	decls, err := lexer.lex([]byte(query)) // declarations
	if err != nil {
		t.Fatalf("Cannot lex <%s> string: %s", query, err)
	}

	instructions, err := parser.parse(decls)
	if err != nil {
		t.Fatalf("Cannot parse tokens from '%s': %s", query, err)
	}

	if len(instructions) != instructionNumber {
		t.Fatalf("Should have parsed %d instructions, got %d", instructionNumber, len(instructions))
	}

	return instructions
}

var deep string

func TestCreate1(t *testing.T) {
	query := `CREATE TABLE IF NOT EXISTS tblShuoGG(
    id         BIGINT(20) NOT NULL,
    a_type  VARCHAR(16)         NOT NULL,
    b_value VARCHAR(128)        NOT NULL,
    tag        VARCHAR(256),
    status     tinyint             NOT NULL,
    ctime      INT UNSIGNED  NOT NULL
)
`
	ins := parse(query, 1, t)
	for _, v := range ins {
		walk(t, v.Decls)
	}
}
func walk(t *testing.T, decls []*Decl) {
	if len(decls) == 0 {
		return
	}
	for _, v := range decls {
		t.Log(deep, v.Token, v.Lexeme)
		walk(t, v.Decl)
		deep += "-"
	}
}
