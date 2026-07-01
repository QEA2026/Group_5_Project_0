package models;

/* WHAT is a DTO? Data Transfer Object. It's meant to model some data that
 * doesn't match a DB table. In this case we need a Class that can hold the user-inputted username/password
 * when they login. The username/password that the user enters will get stored in a loginDTO object.
 * You NEVER store a DTO in a database. It's strictly for data transfer from the frontend/backend
*/

public class LoginDTO {
    //TODO: update to username and password
    private String first_name;
    private String last_name;

    public LoginDTO() {
    }

    public LoginDTO(String first_name, String last_name) {
        this.first_name = first_name;
        this.last_name = last_name;
    }

    public String getFirst_name() {
        return first_name;
    }

    public void setFirst_name(String first_name) {
        this.first_name = first_name;
    }

    public String getLast_name() {
        return last_name;
    }

    public void setLast_name(String last_name) {
        this.last_name = last_name;
    }
}
