-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 10, 2022 at 11:58 AM
-- Server version: 10.4.22-MariaDB
-- PHP Version: 7.4.27

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `rumah123scraper`
--

-- --------------------------------------------------------

--
-- Table structure for table `rumah123`
--

CREATE TABLE `rumah123` (
  `id` int(11) NOT NULL,
  `channel` varchar(24) NOT NULL,
  `property_id` varchar(10) NOT NULL,
  `property_type` varchar(24) NOT NULL,
  `province` varchar(32) NOT NULL,
  `regency` varchar(32) NOT NULL,
  `subdistrict` varchar(32) DEFAULT NULL,
  `title` varchar(64) DEFAULT NULL,
  `built_up` int(11) DEFAULT NULL,
  `land_area` int(11) DEFAULT NULL,
  `bedroom` int(11) DEFAULT NULL,
  `bathroom` int(11) DEFAULT NULL,
  `furnishing` varchar(32) DEFAULT NULL,
  `conditions` varchar(32) DEFAULT NULL,
  `floor` int(11) DEFAULT NULL,
  `certificate` varchar(48) DEFAULT NULL,
  `electricity` varchar(24) DEFAULT NULL,
  `completion_date` varchar(24) DEFAULT NULL,
  `price` int(11) DEFAULT NULL,
  `price_unit` varchar(24) DEFAULT NULL,
  `transacted` varchar(32) DEFAULT NULL,
  `agent_id` varchar(64) DEFAULT NULL,
  `agent_name` varchar(48) NOT NULL,
  `agency` varchar(120) DEFAULT NULL,
  `url` varchar(99) NOT NULL,
  `agent_url` varchar(99) NOT NULL,
  `update_timestamp` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `rumah123temp`
--

CREATE TABLE `rumah123temp` (
  `id` int(11) NOT NULL,
  `url` varchar(120) NOT NULL,
  `update_timestamp` date NOT NULL,
  `response` text NOT NULL,
  `visited` int(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `rumah123`
--
ALTER TABLE `rumah123`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `rumah123temp`
--
ALTER TABLE `rumah123temp`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `rumah123`
--
ALTER TABLE `rumah123`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;

--
-- AUTO_INCREMENT for table `rumah123temp`
--
ALTER TABLE `rumah123temp`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
