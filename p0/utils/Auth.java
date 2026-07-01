package utils;

import DAO.UserDAO;
import models.User;

public class Auth {
    public static String login(String username, String password){
        User user = new UserDAO().getUserByUsername(username);
        if(user != null){
            if(user.getPassword().equals(password)){
                String token = JwtUtil.generateToken(user.getId(), user.getRole());
                return token;
            }
            if(!user.getPassword().equals(password)){
                System.out.println("Incorrect Login");
            }
        }
        else{
            System.out.println("No user found for that login");
        }
        return null;
    }
}
