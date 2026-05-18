#include <stdio.h>
#include <complex.h>   // Karmaşık sayılar için kütüphane (Library for complex numbers)

int main() {
    double p = 0.5; // Örnek parametre (hata fazı) (Example parameter: error phase)

    // Hata operatörü E(p) (Error operator E(p))
    // E(p) = [[1, 0], [0, e^{ip}]]
    double complex E[2][2] = {{1, 0}, {0, cexp(I*p)}};

    // Düzeltme operatörü C(p) (Correction operator C(p))
    // C(p) = [[1, 0], [0, e^{-ip}]]
    double complex C[2][2] = {{1, 0}, {0, cexp(-I*p)}};

    // Sonuç matrisi R = C * E (Result matrix R = C * E)
    double complex R[2][2];

    // Matris çarpımı (2x2 matrisler için) (Matrix multiplication for 2x2 matrices)
    for(int i=0;i<2;i++){
        for(int j=0;j<2;j++){
            R[i][j] = 0; // Başlangıç değeri (Initial value)
            for(int k=0;k<2;k++){
                R[i][j] += C[i][k]*E[k][j]; // Çarpım ve toplama (Multiplication and addition)
            }
        }
    }

    // Sonucu ekrana yazdır (Print the result to screen)
    // Beklenen sonuç: Birim matris [[1,0],[0,1]] (Expected result: Identity matrix [[1,0],[0,1]])
    printf("Result matrix:\n");
    for(int i=0;i<2;i++){
        for(int j=0;j<2;j++){
            printf("%f + %fi  ", creal(R[i][j]), cimag(R[i][j])); 
            // Gerçek ve sanal kısmı yazdır (Print real and imaginary parts)
        }
        printf("\n");
    }

    return 0; // Program sonu (End of program)
}
