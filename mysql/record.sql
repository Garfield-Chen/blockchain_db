/*
Navicat MySQL Data Transfer

Source Server         : blockchain_demo
Source Server Version : 80012
Source Host           : localhost:3306
Source Database       : blockchain_demo

Target Server Type    : MYSQL
Target Server Version : 80012
File Encoding         : 65001

Date: 2019-08-14 17:07:34
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for record
-- ----------------------------
DROP TABLE IF EXISTS `record`;
CREATE TABLE `record` (
  `uid` int(11) NOT NULL AUTO_INCREMENT,
  `user` varchar(255) NOT NULL,
  `date` datetime NOT NULL,
  `assert` varchar(255) NOT NULL,
  `block` varchar(255) NOT NULL,
  `operate` varchar(255) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
