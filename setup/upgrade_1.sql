-- _s means status schreiben
-- _g means status gegengelesen
-- _f means status freigegeben
ALTER TABLE reports ADD COLUMN jaccard_s_f real,
                    ADD COLUMN jaccard_g_f real,
                    ADD COLUMN words_added_s_f smallint,
                    ADD COLUMN words_added_g_f smallint,
                    ADD COLUMN words_deleted_s_f smallint,
                    ADD COLUMN words_deleted_g_f smallint,
                    ADD COLUMN total_words_s smallint,
                    ADD COLUMN total_words_g smallint,
                    ADD COLUMN total_words_f smallint;
