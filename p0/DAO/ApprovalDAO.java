package DAO;

import models.Expense;
import utils.ConnectionUtil;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.time.LocalDate;

public class ApprovalDAO {
    public void approveOrDeny(int id, String status, String comment, int reviewer_id) {

        try (Connection conn = ConnectionUtil.getConnection()) {
            String sql = "UPDATE approvals SET status = ?, reviewer = ?, comment = ?, review_date = ? where expense_id = ?;";

            PreparedStatement ps = conn.prepareStatement(sql);
            ps.setString(1, status);
            ps.setInt(2, reviewer_id);
            ps.setString(3, comment);
            ps.setString(4, LocalDate.now().toString());
            ps.setInt(5, id);
            ps.executeUpdate();




        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }
}
