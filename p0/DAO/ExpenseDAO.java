package DAO;

import models.Expense;
import utils.ConnectionUtil;

import java.sql.*;
import java.util.ArrayList;

public class ExpenseDAO {

    public ArrayList<Expense> getExpensesByUserID(int userID) {
        try (Connection conn = ConnectionUtil.getConnection()) {
            String sql = "select * from expenses where user_id = ?;";

            PreparedStatement ps = conn.prepareStatement(sql);
            ps.setInt(1, userID);
            ResultSet rs = ps.executeQuery();
            ArrayList<Expense> expenseList = new ArrayList<>();

            while (rs.next()) {
                Expense e = new Expense(
                        rs.getInt("id"),
                        rs.getInt("user_id"),
                        rs.getFloat("amount"),
                        rs.getString("description"),
                        rs.getString("date")
                );
                expenseList.add(e);
            }
            return expenseList;

        } catch (SQLException e) {
            throw new RuntimeException(e);
        }


    }
    public ArrayList<Expense> getExpensesByDate(String date) {
        try (Connection conn = ConnectionUtil.getConnection()) {
            String sql = "select * from expenses where date = ?;";

            PreparedStatement ps = conn.prepareStatement(sql);
            ps.setString(1, date);
            ResultSet rs = ps.executeQuery();
            ArrayList<Expense> expenseList = new ArrayList<>();

            while (rs.next()) {
                Expense e = new Expense(
                        rs.getInt("id"),
                        rs.getInt("user_id"),
                        rs.getFloat("amount"),
                        rs.getString("description"),
                        rs.getString("date")
                );
                expenseList.add(e);
            }
            return expenseList;

        } catch (SQLException e) {
            throw new RuntimeException(e);
        }


    }
    public ArrayList<Expense> getExpensesByStatus(String stat) {
        stat = stat.toLowerCase();
        try (Connection conn = ConnectionUtil.getConnection()) {
            String sql = "select e.id, e.user_id, e.amount, e.description, e.date from expenses e " +
                    "join approvals a ON a.expense_id = e.id " +
                    "where a.status = ?;";

            PreparedStatement ps = conn.prepareStatement(sql);
            ps.setString(1, stat);
            ResultSet rs = ps.executeQuery();
            ArrayList<Expense> expenseList = new ArrayList<>();

            while (rs.next()) {
                Expense e = new Expense(
                        rs.getInt("id"),
                        rs.getInt("user_id"),
                        rs.getFloat("amount"),
                        rs.getString("description"),
                        rs.getString("date")
                );
                expenseList.add(e);
            }
            return expenseList;

        } catch (SQLException e) {
            throw new RuntimeException(e);
        }


    }

    public ArrayList<Expense> getExpensesByDateRange(String start_date, String end_date) {
        try (Connection conn = ConnectionUtil.getConnection()) {
            String sql = "select * from expenses where date between ? AND ?;";

            PreparedStatement ps = conn.prepareStatement(sql);
            ps.setString(1, start_date);
            ps.setString(2, end_date);
            ResultSet rs = ps.executeQuery();
            ArrayList<Expense> expenseList = new ArrayList<>();

            while (rs.next()) {
                Expense e = new Expense(
                        rs.getInt("id"),
                        rs.getInt("user_id"),
                        rs.getFloat("amount"),
                        rs.getString("description"),
                        rs.getString("date")
                );
                expenseList.add(e);
            }
            return expenseList;

        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }




    public ArrayList<Expense> getPendingExpenses(){
        try (Connection conn = ConnectionUtil.getConnection()){
            String sql = "SELECT e.id, e.user_id, e.amount, e.description, e.date" +
                    " FROM expenses e" +
                    " JOIN approvals a ON a.expense_id = e.id" +
                    " WHERE a.status = 'pending'; ";

            Statement st = conn.createStatement();
            ResultSet rs = st.executeQuery(sql);

            ArrayList<Expense> expenseList = new ArrayList<>();

            while(rs.next()){
                Expense e = new Expense(
                        rs.getInt("id"),
                        rs.getInt("user_id"),
                        rs.getFloat("amount"),
                        rs.getString("description"),
                        rs.getString("date")
                );
                expenseList.add(e);
            }
            return expenseList;

        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

}
