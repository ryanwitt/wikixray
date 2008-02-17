-- Core of the wiki: each page has an entry here which identifies
-- it by title and contains some essential metadata.
--
CREATE TABLE /*$wgDBprefix*/page (
  -- Unique identifier number. The page_id will be preserved across
  -- edits and rename operations, but not deletions and recreations.
  page_id int unsigned NOT NULL ,
  
  -- A page name is broken into a namespace and a title.
  -- The namespace keys are UI-language-independent constants,
  -- defined in includes/Defines.php
  page_namespace int NOT NULL,
  
  -- The rest of the title, as text.
  -- Spaces are transformed into underscores in title storage.
  page_title varchar(255) binary NOT NULL,
  
  -- Handy key to revision.rev_id of the current revision.
  -- This may be 0 during page creation, but that shouldn't
  -- happen outside of a transaction... hopefully.
  page_latest int unsigned NOT NULL,
  
  -- Uncompressed length in bytes of the page's current source text.
  page_len int unsigned NOT NULL,
  -- 1 indicates the article is a redirect.
  page_is_redirect tinyint unsigned NOT NULL default '0',
  
  -- 1 indicates the article is a stub.
  page_is_stub tinyint unsigned NOT NULL default '0',
  -- Random value between 0 and 1, used for Special:Randompage
  page_random real unsigned NOT NULL,
  -- 1 indicates this is a new entry, with only one edit.
  -- Not all pages with one edit are new pages.
  page_is_new tinyint unsigned NOT NULL default '0',
  
  -- Comma-separated set of permission keys indicating who
  -- can move or edit the page.
  page_restrictions tinyblob NOT NULL default '',

  PRIMARY KEY page_id (page_id)
) /*$wgDBTableOptions*/;

--
-- Every edit of a page creates also a revision row.
-- This stores metadata about the revision, and a reference
-- to the text storage backend.
--
CREATE TABLE /*$wgDBprefix*/revision (
  rev_id int unsigned NOT NULL ,
  
  -- Key to page_id. This should _never_ be invalid.
  rev_page int unsigned NOT NULL,
  
  -- Key to user.user_id of the user who made this edit.
  -- Stores 0 for anonymous edits and for some mass imports.
  rev_user int unsigned NOT NULL default '0',
  
  -- Text username or IP address of the editor.
  rev_user_text varchar(255) binary NOT NULL default '',
  
  -- Timestamp
  rev_timestamp binary(19) NOT NULL default '',
  
  -- Uncompressed length in bytes of the revision's current source text.
  rev_len int NOT NULL,
  -- Number of letters of the revision's current source text.
  rev_num_letters int NOT NULL,
  -- Number of words of the revision's current source text.
  rev_num_words int NOT NULL,
  -- Number of highlighted words
  rev_num_highwords int NOT NULL,
  -- Number of special links
  rev_num_special int NOT NULL,
  -- Number of internal links
  rev_num_inlinks int NOT NULL,
  -- Number of external links
  rev_num_outlinks int NOT NULL,
  -- Number of translations to other language editions
  rev_num_trans int NOT NULL,
  -- Number of sections
  rev_num_sections int NOT NULL,
  -- Key to revision.rev_id
  -- This field is used to add support for a tree structure (The Adjacency List Model)
  rev_parent_id int unsigned default NULL,
  -- Records whether this revision is a redirect
  rev_is_redirect tinyint unsigned NOT NULL default '0',
  -- Records wheter this revision is a stub
  rev_is_stub tinyint unsigned NOT NULL default '0',
  -- Records whether the user marked the 'minor edit' checkbox.
  -- Many automated edits are marked as minor.
  rev_minor_edit tinyint unsigned NOT NULL default '0',
  
  -- Text comment summarizing the change.
  -- This text is shown in the history and other changes lists,
  -- rendered in a subset of wiki markup by Linker::formatComment()
  rev_comment tinyblob NOT NULL default '',

  PRIMARY KEY rev_page_id (rev_page, rev_id),
  UNIQUE INDEX rev_id (rev_id)
) /*$wgDBTableOptions*/ MAX_ROWS=100000000 AVG_ROW_LENGTH=1024;

--Special table storing info about namespaces
CREATE TABLE namespaces (
  name varchar(30),
  code int(3),
  PRIMARY KEY name (name)
);

--Table for highlighted words in each revision
CREATE TABLE highlight (
  highword_id int unsigned NOT NULL,
  -- Highlighted text
  highword_text text NOT NULL default '',
  PRIMARY KEY highword_id (highword_id)
)MAX_ROWS=100000000 AVG_ROW_LENGTH=1024;

-- Intermediate table linking highword_id with multiple rev_id
CREATE TABLE rev_highlight (
  -- Foreing key to rev_id
  rev_id int unsigned NOT NULL ,
  highword_id int unsigned NOT NULL
)MAX_ROWS=100000000 AVG_ROW_LENGTH=1024;

--Table for special links in each revision
CREATE TABLE special (
  special_id int unsigned NOT NULL ,
  -- Special links
  special_text text NOT NULL default '',
  PRIMARY KEY special_id (special_id)
)MAX_ROWS=100000000 AVG_ROW_LENGTH=1024;

-- Intermediate table linking highword_id with multiple rev_id
CREATE TABLE rev_special (
  -- Foreing key to rev_id
  rev_id int unsigned NOT NULL,
  special_id int unsigned NOT NULL
)MAX_ROWS=100000000 AVG_ROW_LENGTH=1024;

--Table for inlinks links in each revision
CREATE TABLE inlink (
  inlink_id int unsigned NOT NULL ,
  -- Special links
  inlink_text text NOT NULL default '',
  PRIMARY KEY inlink_id (inlink_id)
)MAX_ROWS=100000000 AVG_ROW_LENGTH=1024;

-- Intermediate table linking inlink_id with multiple rev_id
CREATE TABLE rev_inlink (
  -- Foreing key to rev_id
  rev_id int unsigned NOT NULL,
  inlink_id int unsigned NOT NULL
)MAX_ROWS=100000000 AVG_ROW_LENGTH=1024;

--Table for special links in each revision
CREATE TABLE outlink (
  outlink_id int unsigned NOT NULL ,
  -- Special links
  outlink_text text NOT NULL default '',
  PRIMARY KEY outlink_id (outlink_id)
)MAX_ROWS=100000000 AVG_ROW_LENGTH=1024;

-- Intermediate table linking outlink_id with multiple rev_id
CREATE TABLE rev_outlink (
  -- Foreing key to rev_id
  rev_id int unsigned NOT NULL,
  outlink_id int unsigned NOT NULL
)MAX_ROWS=100000000 AVG_ROW_LENGTH=1024;

--Table for translations links in each revision
CREATE TABLE trans (
  trans_id int unsigned NOT NULL ,
  -- Special links
  trans_text text NOT NULL default '',
  PRIMARY KEY trans_id (trans_id)
)MAX_ROWS=100000000 AVG_ROW_LENGTH=1024;

-- Intermediate table linking translation_id with multiple rev_id
CREATE TABLE rev_trans (
  -- Foreing key to rev_id
  rev_id int unsigned NOT NULL,
  trans_id int unsigned NOT NULL
)MAX_ROWS=100000000 AVG_ROW_LENGTH=1024;
