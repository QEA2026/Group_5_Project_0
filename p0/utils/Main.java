package utils;

import DAO.ApprovalDAO;
import DAO.ExpenseDAO;
//import DAO.RoleDAO;
import io.jsonwebtoken.Claims;
import models.Expense;


import java.util.ArrayList;
import java.util.Scanner;

public class Main {
    static int reviewerId = -1;
    public static void main(String[] args) {

        Scanner sc = new Scanner(System.in);

        boolean login_success = login(sc);

        if(login_success == true){

            while (login_success == true) {
                //Generate Main Menu
                generateMenu();
                int cmd = sc.nextInt();

                //Option 1: View all expenses
                if (cmd == 1) {
                    ArrayList<Expense> pending =  new ExpenseDAO().getPendingExpenses();
                    printExpenses(pending);

                }

                //Option 2: Generate report
                else if(cmd == 2){

                    boolean report = true;

                    while(report == true){
                        System.out.println("How would you like to generate your report?");
                        System.out.println(" ");
                        System.out.println("1. By Employee");
                        System.out.println("2. By Date");
                        System.out.println("3. By Status");
                        System.out.println("4. Exit");


                        //GENERATE REPORTR
                        int next_cmd = sc.nextInt();
                        sc.nextLine();
                        if(next_cmd == 1){
                            System.out.println("Input employee ID: ");
                            int emp_id = sc.nextInt();
                            ArrayList<Expense> pending =  new ExpenseDAO().getExpensesByUserID(emp_id);
                            printExpenses(pending);

                            System.out.println("Would you like to approve or deny any expenses?:");
                            System.out.println("");
                            System.out.println("1. Yes");
                            System.out.println("2. No");
                            int y_Or_n = sc.nextInt();
                            sc.nextLine();
                            if(y_Or_n == 1){
                                System.out.println("Which expense would you like to edit? Please input the expense ID: ");
                                int expense_id = sc.nextInt();
                                sc.nextLine();
                                approveOrDenyPrompt(sc, expense_id);
                            }
                        }


                        else if (next_cmd == 2){
                            System.out.println("Between which dates would you like to search?");
                            System.out.println("Start Date (YYYY-MM-DD): ");
                            String start_date = sc.nextLine();

                            System.out.println("End Date(YYYY-MM-DD): ");
                            String end_date = sc.nextLine();

                            ArrayList<Expense> pending_by_date =  new ExpenseDAO().getExpensesByDateRange(start_date, end_date);
                            printExpenses(pending_by_date);

                            System.out.println("Would you like to approve or deny any expenses?:");
                            System.out.println("");
                            System.out.println("1. Yes");
                            System.out.println("2. No");
                            int y_Or_n = sc.nextInt();
                            sc.nextLine();
                            if(y_Or_n == 1){
                                System.out.println("Which expense would you like to edit? Please input the expense ID: ");
                                int expense_id = sc.nextInt();
                                sc.nextLine();
                                approveOrDenyPrompt(sc, expense_id);
                            }


                        }
                        else if(next_cmd == 3){
                            System.out.println("Which status would you like to see?");
                            System.out.println("    ");
                            System.out.println("1. Pending");
                            System.out.println("2. Approved");
                            System.out.println("3. Denied");
                            int stat_report = sc.nextInt();
                            sc.nextLine();

                            if(stat_report == 1){
                                ArrayList<Expense> pending_by_status =  new ExpenseDAO().getExpensesByStatus("Pending");
                                printExpenses(pending_by_status);

                            }
                            if(stat_report == 2){
                                ArrayList<Expense> pending_by_status =  new ExpenseDAO().getExpensesByStatus("Approved");
                                printExpenses(pending_by_status);
                            }
                            if(stat_report == 3){
                                ArrayList<Expense> pending_by_status =  new ExpenseDAO().getExpensesByStatus("Denied");
                                printExpenses(pending_by_status);
                            }

                            System.out.println("Would you like to approve or deny any expenses?:");
                            System.out.println("");
                            System.out.println("1. Yes");
                            System.out.println("2. No");
                            int y_Or_n = sc.nextInt();
                            sc.nextLine();
                            if(y_Or_n == 1){
                                System.out.println("Which expense would you like to edit? Please input the expense ID: ");
                                int expense_id = sc.nextInt();
                                sc.nextLine();
                                approveOrDenyPrompt(sc, expense_id);
                            }

                        }
                        else if(next_cmd == 4){
                            System.out.println("Exiting");
                            report = false;
                        }
                        else{
                            System.out.println("Code not recognized, please try again!");
                        }
                    }


                }

                //Option 3: Approve or Deny
                else if (cmd == 3) {
                    System.out.println("What expense would you like to edit? Input expense ID: ");
                    int expense_id = sc.nextInt();
                    sc.nextLine();
                    System.out.println("Would you like to Approve or Deny this expense?");
                    System.out.println("");
                    System.out.println("1. Approve");
                    System.out.println("2. Deny");
                    System.out.println("3. Quit");
                    int approve_or_deny = sc.nextInt();
                    sc.nextLine();

                    if(approve_or_deny == 1){
                        String status = "Approved";
                        System.out.println("If you would like, leave a comment here: ");
                        String comment = sc.nextLine();
                        new ApprovalDAO().approveOrDeny(expense_id, status, comment, reviewerId);
                    }
                    else if(approve_or_deny == 2){
                        String status = "Denied";
                        System.out.println("If you would like, leave a comment here: ");
                        String comment = sc.nextLine();
                        new ApprovalDAO().approveOrDeny(expense_id, status, comment, reviewerId);
                    }
                    else if(approve_or_deny == 3){
                        continue;
                    }




                }

                //Option 4: Logout
                else if (cmd == 4) {
                    login_success = false;
                }
                else if(cmd == 5){
                    System.out.println("Quitting");
                    System.exit(0);
                }
                else{
                    System.out.println("Command not recognized, please try again");
                }
            }
        }
        else{
            System.out.println("Login failed");

        }
    }


    public static boolean login( Scanner sc) {

        System.out.println("=====================");
        boolean logged_in = false;
        int login_cnt = 0;

        while (logged_in != true && login_cnt < 3) {
            System.out.println("Username: ");
            String username = sc.nextLine();
            System.out.println("Password: ");
            String password = sc.nextLine();

            String token = new Auth().login(username, password);
            if (token != null) {
                // verify the token
                Claims claims = JwtUtil.verifyToken(token);
                if (claims != null) {
                    System.out.println("Welcome " + username);
                    reviewerId = claims.get("employee_id", Integer.class);
                    logged_in = true;
                    return logged_in;
                }
            } else {
                login_cnt++;
                System.out.println("Incorrect username or password, please try again");
            }
        }
            System.out.println("Too many failed login attempts, please rerun the program and try again.");
            return logged_in;

    }

        //Method to show main app menu
        public static void generateMenu() {
            System.out.println("=====================");
            System.out.println("Manager Application Menu");
            System.out.println("=====================");
            System.out.println(" ");
            System.out.println("What would you like to do? ");
            System.out.println("1. View all expenses");
            System.out.println("2. Generate report");
            System.out.println("3. Approve/Deny an expense");
            System.out.println("4. Logout");
            System.out.println("5. Exit");
        }



        public static void printExpenses(ArrayList<Expense> expenses){
        System.out.println("ID     User ID     Amount     Description         Date");
            for (Expense e : expenses) {
                System.out.printf("%-7d%-12d%-11.2f%-20s%-6s%n", e.getId(), e.getUser_id(), e.getAmount(), e.getDescription(), e.getDate());
            }
        }
        public static void approveOrDenyPrompt(Scanner sc, int expense_id){
            System.out.println("Would you like to Approve or Deny this expense?");
            System.out.println("");
            System.out.println("1. Approve");
            System.out.println("2. Deny");
            System.out.println("3. Quit");
            int approve_or_deny = sc.nextInt();
            sc.nextLine();

            if(approve_or_deny == 1){
                String status = "Approved";
                System.out.println("If you would like, leave a comment here: ");
                String comment = sc.nextLine();
                new ApprovalDAO().approveOrDeny(expense_id, status, comment, reviewerId);
                System.out.println("Expense " + expense_id + "approved");
            }
            else if(approve_or_deny == 2){
                String status = "Denied";
                System.out.println("If you would like, leave a comment here: ");
                String comment = sc.nextLine();
                new ApprovalDAO().approveOrDeny(expense_id, status, comment, reviewerId);
                System.out.println("Expense " + expense_id + "denied");
            }

        }
    }
