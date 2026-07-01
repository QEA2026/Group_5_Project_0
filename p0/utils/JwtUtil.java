package utils;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;

import javax.crypto.SecretKey;
import java.util.Date;

public class JwtUtil {
    private static final SecretKey SECRET_KEY = Keys.secretKeyFor(io.jsonwebtoken.SignatureAlgorithm.HS256);

    //lasts for 1 hour
    private static final long EXPIRATION_TIME = 1000 * 60 * 60;

    public static String generateToken(int employeeID, String role){
        Date now = new Date();
        Date expire = new Date(now.getTime() + EXPIRATION_TIME);

        return Jwts.builder()
                .claim("employee_id", employeeID)
                .claim("role", role)
                .issuedAt(now)
                .expiration(expire)
                .signWith(SECRET_KEY)
                .compact();
    }

    public static Claims verifyToken(String token){
        try{
            return Jwts.parser()
                    .verifyWith(SECRET_KEY)
                    .build()
                    .parseSignedClaims(token)
                    .getPayload();
        } catch (ExpiredJwtException e){
            System.out.println("Token has expired");
            return null;
        } catch (JwtException e){
            System.out.println("Invalid Token!");
            return null;
        }

    }
}
