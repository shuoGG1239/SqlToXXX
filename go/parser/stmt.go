package parser

type CreateTableStmt struct {
	IfNotExists bool
	TableName   string
	Cols        []*ColumnDef
	Constraints []*Constraint
	Options     []*TableOption
}

type TableOption struct {
	Tp        TableOptionType
	Default   bool
	StrValue  string // InnoDB utf8
	UintValue uint64 // for AutoIncrement to set the beginning value
}

type ColumnDef struct {
	Name    string
	Tp      *FieldType      // INT VARCHAR TINYINT
	Options []*ColumnOption // AutoIncrement NotNull
}

type Constraint struct {
	Tp   ConstraintType
	Name string
	Keys []string
}

type ColumnOption struct {
	Tp      ColumnOptionType
	Default DefValue
}

type DefValue struct {
}

// ColumnOptionType is the type for ColumnOption.
type ColumnOptionType int

// ColumnOption types.
const (
	ColumnOptionNoOption ColumnOptionType = iota
	ColumnOptionPrimaryKey
	ColumnOptionNotNull
	ColumnOptionAutoIncrement
	ColumnOptionDefaultValue
	ColumnOptionUniqKey
	ColumnOptionNull
	ColumnOptionOnUpdate // For Timestamp and Datetime only.
	ColumnOptionFulltext
	ColumnOptionComment
	ColumnOptionGenerated
	ColumnOptionReference
	ColumnOptionCollate
	ColumnOptionCheck
	ColumnOptionColumnFormat
	ColumnOptionStorage
)

// ConstraintType is the type for Constraint.
type ConstraintType int

// ConstraintTypes
const (
	ConstraintNoConstraint ConstraintType = iota
	ConstraintPrimaryKey
	ConstraintKey
	ConstraintIndex
	ConstraintUniq
	ConstraintUniqKey
	ConstraintUniqIndex
	ConstraintForeignKey
	ConstraintFulltext
	ConstraintCheck
)

type FieldType struct {
	Tp      byte
	Flag    uint
	Flen    int
	Decimal int
	Charset string
	Collate string
	Elems   []string // for ENUM
}

// TableOptionType is the type for TableOption
type TableOptionType int

// TableOption types.
const (
	TableOptionNone TableOptionType = iota
	TableOptionEngine
	TableOptionCharset
	TableOptionCollate
	TableOptionAutoIncrement
	TableOptionComment
	TableOptionAvgRowLength
	TableOptionCheckSum
	TableOptionCompression
	TableOptionConnection
	TableOptionPassword
	TableOptionKeyBlockSize
	TableOptionMaxRows
	TableOptionMinRows
	TableOptionDelayKeyWrite
	TableOptionRowFormat
	TableOptionStatsPersistent
	TableOptionStatsAutoRecalc
	TableOptionShardRowID
	TableOptionPreSplitRegion
	TableOptionPackKeys
	TableOptionTablespace
	TableOptionNodegroup
	TableOptionDataDirectory
	TableOptionIndexDirectory
	TableOptionStorageMedia
	TableOptionStatsSamplePages
	TableOptionSecondaryEngine
	TableOptionSecondaryEngineNull
	TableOptionInsertMethod
	TableOptionTableCheckSum
	TableOptionUnion
	TableOptionEncryption
)
