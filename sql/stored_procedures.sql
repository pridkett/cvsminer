-- removes a particular mail archive from the database
-- usage:
--   select remove_mail_file_archive("xml-2004-august.gz");
CREATE OR REPLACE FUNCTION remove_mail_file_archive(text) RETURNS INTEGER AS '
  DECLARE
    archivename ALIAS FOR $1;
    archive_rec RECORD;
  BEGIN
    SELECT INTO archive_rec * FROM mail_file_archive WHERE filename = archivename;
    IF NOT FOUND THEN
        RAISE EXCEPTION ''archive % not found'', archivename;
    END IF;
    UPDATE mail_message SET message_parent = NULL WHERE mail_message_id IN
      (SELECT a.mail_message_id FROM mail_message a, mail_message b
        WHERE b.mail_file_archive_id = archive_rec.mail_file_archive_id
          AND a.mail_file_archive_id <> b.mail_file_archive_id
          AND a.message_parent=b.mail_message_id);
    DELETE FROM mail_message_to WHERE mail_message_to.mail_message_id IN
           (SELECT mail_message_id FROM mail_message
             WHERE mail_message.mail_file_archive_id = archive_rec.mail_file_archive_id);
    DELETE FROM mail_message_reference WHERE mail_message_reference.mail_message_id IN
           (SELECT mail_message_id FROM mail_message
             WHERE mail_message.mail_file_archive_id = archive_rec.mail_file_archive_id);
    DELETE FROM mail_message WHERE mail_file_archive_id = archive_rec.mail_file_archive_id;
    DELETE FROM mail_file_archive WHERE mail_file_archive_id = archive_rec.mail_file_archive_id;
    RETURN 1;
  END;
' LANGUAGE plpgsql;

-- removes all traces of a particular list from the database
-- usage:
--   select drop_mail_list('xml');
CREATE OR REPLACE FUNCTION drop_mail_list(text) RETURNS INTEGER AS '
  DECLARE
    listname ALIAS FOR $1;
    dl RECORD;
  BEGIN
    SELECT INTO dl * FROM mailing_list WHERE name = listname;
    IF NOT FOUND THEN
      RAISE EXCEPTION ''list % not found'', listname;
    END IF;
    UPDATE mail_message SET message_parent = NULL WHERE  mail_message_id IN
      (SELECT a.mail_message_id FROM mail_message a, mail_message b
        WHERE b.mailing_list_id = dl.mailing_list_id
          AND a.mailing_list_id <> b.mailing_list_id
          AND a.message_parent=b.mail_message_id);
    DELETE FROM mail_message_to WHERE EXISTS (SELECT mail_message.mail_message_id FROM mail_message
                                               WHERE mail_message_to.mail_message_id = mail_message.mail_message_id
                                                     AND mail_message.mailing_list_id = dl.mailing_list_id);
    DELETE FROM mail_message_reference WHERE EXISTS (SELECT mail_message.mail_message_id FROM mail_message
                                                      WHERE mail_message_reference.mail_message_id = mail_message.mail_message_id
                                                        AND mail_message.mailing_list_id = dl.mailing_list_id);
    DELETE FROM mail_message WHERE mailing_list_id = dl.mailing_list_id;
    DELETE FROM mail_file_archive WHERE mailing_list_id = dl.mailing_list_id;
    DELETE FROM mailing_list WHERE mailing_list_id = dl.mailing_list_id;
    RETURN 1;
  END;
' LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION bz_bugs_activity_response_new() RETURNS TRIGGER AS '
DECLARE
BEGIN
ALTER TABLE bz_bugs_activity DISABLE TRIGGER bz_bugs_activity_update_response_trigger;
IF(TG_OP=''INSERT'') THEN
    UPDATE bz_bugs_activity SET added_id=NEW.id WHERE added=NEW.value;
    UPDATE bz_bugs_activity SET removed_id=NEW.id WHERE removed=NEW.value;
ELSIF(TG_OP=''UPDATE'') THEN
    UPDATE bz_bugs_activity SET added_id=NULL WHERE added_id=OLD.id;
    UPDATE bz_bugs_activity SET removed_id=NULL WHERE removeD_id=OLD.id;
    UPDATE bz_bugs_activity SET added_id=NEW.id WHERE added=NEW.value;
    UPDATE bz_bugs_activity SET removed_id=NEW.id WHERE removed=NEW.value;
ELSIF(TG_OP=''DELETE'') THEN
    UPDATE bz_bugs_activity SET added_id=NULL WHERE added_id=OLD.id;
    UPDATE bz_bugs_activity SET removed_id=NULL WHERE removed_id=OLD.id;
END IF;
ALTER TABLE bz_bugs_activity ENABLE TRIGGER bz_bugs_activity_update_response_trigger;
RETURN NEW;
END;
' LANGUAGE plpgsql;
CREATE TRIGGER bz_bugs_activity_response_new_trigger AFTER INSERT OR UPDATE OR DELETE ON bz_bugs_activity_response FOR EACH ROW EXECUTE PROCEDURE bz_bugs_activity_response_new();

CREATE OR REPLACE FUNCTION bz_bugs_activity_update_response() RETURNS TRIGGER AS '
DECLARE
    response_id AS int;
BEGIN
IF (TG_OP=''INSERT'' OR TG_OP=''UPDATE'') THEN
    SELECT id INTO response_id FROM bz_bugs_activity_response WHERE value=NEW.added;
    IF (FOUND) THEN
        UPDATE bz_bugs_activity SET added_id=response_id WHERE bz_bugs_activity_id=response_id;
    END IF;
    SELECT id INTO response_id FROM bz_bugs_activity_response WHERE value=NEW.removed;
    IF (FOUND) THEN
        UPDATE bz_bugs_activity SET removed_id=response_id WHERE bz_bugs_activity_id=response_id;
    END IF;
END IF;
RETURN NEW;
END;
' LANGUAGE plpgsql;
CREATE TRIGGER bz_bugs_activity_update_response_trigger AFTER INSERT OR UPDATE OR DELETE ON bz_bugs_activity FOR EACH ROW EXECUTE PROCEDURE bz_bugs_activity_update_response();
