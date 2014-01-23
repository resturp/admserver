/* (Postgre)SQL script for creating the database for the adm-server
   visit us our website at: http://admserver.frii.nl

   Copyright 2014 Thomas Boose
   thomas at boose dot nl.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License. */

CREATE TABLE admassignment
(
  deadline date,
  title character varying(255) NOT NULL,
  description text,
  image path,
  course character varying(255),
  CONSTRAINT "dmassignment-pkey" PRIMARY KEY (title )
)
WITH (
  OIDS=FALSE
);

CREATE TABLE admsolution
(
  assignment character varying(255) NOT NULL,
  tasknr integer NOT NULL,
  email character varying(255) NOT NULL,
  submissionstamp timestamp without time zone NOT NULL,
  code text,
  results text,
  score integer NOT NULL,

  CONSTRAINT submission_key PRIMARY KEY (assignment, tasknr , email , submissionstamp )
)
WITH (
  OIDS=FALSE
);

CREATE TABLE admtask
(
  assignment character varying(255) NOT NULL,
  tasknr integer NOT NULL,
  description text,
  testsuite text,
  attempts integer NOT NULL DEFAULT 0,
  totalscore integer NOT NULL DEFAULT 0,
  CONSTRAINT "task-key" PRIMARY KEY (assignment , tasknr )
)
WITH (
  OIDS=FALSE
);

CREATE TABLE admuser
(
  email character varying(255) NOT NULL,
  password character varying(255),
  isadmin boolean NOT NULL DEFAULT false,
  courses character varying(255),
  nickname character varying(255) DEFAULT 'Ada Lovelace',
  CONSTRAINT pkey PRIMARY KEY (email )
)
WITH (
  OIDS=FALSE
);


INSERT INTO admuser(email, password, isadmin, courses)
    VALUES ('admin@site.local','admin', TRUE, 'first'),('user@site.local','user',FALSE, 'first');

INSERT INTO admassignment(deadline, title, description, course)
    VALUES ('02/15/2014', 'Example assingment', 'This is a simple example assignment to show the ADM server funtionality', 'first');

INSERT INTO admtask(assignment, tasknr, description)
    VALUES ('Example assingment', 1, 'fibonacci');

INSERT INTO admtask(assignment, tasknr, description)
    VALUES ('Example assingment', 2, 'Dice');

CREATE OR REPLACE VIEW admtaskattemptsperemail AS 
 SELECT admsolution.assignment, admsolution.tasknr, admsolution.email, count(*) AS attemptcount
   FROM admsolution
  GROUP BY admsolution.assignment, admsolution.tasknr, admsolution.email;

CREATE OR REPLACE VIEW admsolutionattempts AS 
 SELECT DISTINCT ON (s.assignment::text || ',' || s.tasknr::text || ',' || s.email::text) s.assignment, s.tasknr, s.email, s.submissionstamp, s.code, s.results, s.score, t.attemptcount, k.attempts, k.totalscore, u.nickname
   FROM admsolution s
   JOIN admtaskattemptsperemail t ON s.assignment = t.assignment AND s.tasknr = t.tasknr AND s.email = t.email
   JOIN admtask as k on s.assignment = k.assignment and s.tasknr = k.tasknr
   JOIN admuser as u on s.email = u.email
  ORDER BY s.assignment::text || ',' || s.tasknr::text || ',' || s.email::text, s.submissionstamp DESC;


