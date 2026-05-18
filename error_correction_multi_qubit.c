#include <stdio.h>
#include <complex.h>
#include <math.h>

int main() {
    double p = 0.5; // Example parameter
    double complex E[2][2] = {{1, 0}, {0, cexp(I*p)}};
    double complex C[2][2] = {{1, 0}, {0, cexp(-I*p)}};
    double complex R[2][2];

    // Matrix multiplication
    for(int i=0;i<2;i++){
        for(int j=0;j<2;j++){
            R[i][j] = 0;
            for(int k=0;k<2;k++){
                R[i][j] += C[i][k]*E[k][j];
            }
        }
    }

    // Check if result is identity matrix
    int isIdentity = 1;
    for(int i=0;i<2;i++){
        for(int j=0;j<2;j++){
            double realPart = creal(R[i][j]);
            double imagPart = cimag(R[i][j]);
            if(i==j) {
                if(fabs(realPart-1.0) > 1e-6 || fabs(imagPart) > 1e-6) {
                    isIdentity = 0;
                }
            } else {
                if(fabs(realPart) > 1e-6 || fabs(imagPart) > 1e-6) {
                    isIdentity = 0;
                }
            }
        }
    }

    // ANSI escape codes: green = \033[0;32m, red = \033[0;31m, reset = \033[0m
    if(isIdentity) {
        printf("\033[0;32mResult matrix is Identity:\n[\n"); // Green
    } else {
        printf("\033[0;31mResult matrix is NOT Identity:\n[\n"); // Red
    }

    for(int i=0;i<2;i++){
        printf("  [ ");
        for(int j=0;j<2;j++){
            printf("%f + %fi ", creal(R[i][j]), cimag(R[i][j]));
        }
        printf("]\n");
    }
    printf("]\033[0m\n"); // Reset color

    return 0;
}
