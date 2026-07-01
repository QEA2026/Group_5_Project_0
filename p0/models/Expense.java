package models;

public class Expense {
    private int id;

    private int user_id;

    private float amount;

    private String description;

    private String date;


    public int getId() {
        return id;
    }

    public int getUser_id() {
        return user_id;
    }

    public float getAmount() {
        return amount;
    }

    public String getDescription() {
        return description;
    }

    public String getDate() {
        return date;
    }

    public Expense(int id, int user_id, float amount, String description, String date) {
        this.id = id;
        this.user_id = user_id;
        this.amount = amount;
        this.description = description;
        this.date = date;
    }


}
