package utils;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class ConnectionUtil{
    //url for the database file
    private static final String url = "jdbc:sqlite:employees.db";
    public static Connection getConnection() throws SQLException {
        return DriverManager.getConnection(url);
    }

}
