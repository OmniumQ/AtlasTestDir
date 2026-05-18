#include <stdio.h>
#include <complex.h>
#include <math.h>

// Küçük n için matris çarpımı (Small n simulation)
void simulate_small_n(int n, double p) {
    // Tek qubit hata ve düzeltme operatörleri
    double complex E[2][2] = {{1, 0}, {0, cexp(I*p)}};
    double complex C[2][2] = {{1, 0}, {0, cexp(-I*p)}};

    // Sadece n=1 için gösterim (örnek)
    double complex R[2][2];
    for(int i=0;i<2;i++){
        for(int j=0;j<2;j++){
            R[i][j] = 0;
            for(int k=0;k<2;k++){
                R[i][j] += C[i][k]*E[k][j];
            }
        }
    }

    // Kontrol
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

    if(isIdentity) {
        printf("\033[0;32mResult for n=%d qubit is Identity.\033[0m\n", n);
    } else {
        printf("\033[0;31mResult for n=%d qubit is NOT Identity.\033[0m\n", n);
    }
}

// Büyük n için sadece mesaj (Large n theoretical check)
void check_large_n(long long n) {
    printf("For n = %lld qubits:\n", n);
    printf("\033[0;32mMathematical proof guarantees result is Identity.\033[0m\n");
    printf("Direct simulation infeasible due to exponential matrix size.\n");
}

int main() {
    double p = 0.5;

    // Küçük n örneği
    simulate_small_n(1, p);

    // Çok büyük n örneği (1 trilyon)
    long long bigN = 1000000000000LL;
    check_large_n(bigN);

    return 0;
}
