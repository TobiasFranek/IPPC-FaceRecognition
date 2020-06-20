
-- -----------------------------------------------------
-- Table `camera`.`faces`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `faces` ;

CREATE TABLE IF NOT EXISTS `faces` (
  `id` VARCHAR(255) NOT NULL,
  `name` VARCHAR(255) NULL,
  `known` TINYINT NULL DEFAULT 0,
  `counter` INT NULL DEFAULT 1,
  `last_seen` FLOAT NULL,
  PRIMARY KEY (`id`))
