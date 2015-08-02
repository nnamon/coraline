#include <stdio.h>
#include <stdlib.h>
 
int main() {
  char * buffer = 0;
  long length;
  FILE * fp = fopen("crashed.txt", "r");
  char badbuffer[20];
 
  if (fp) {
    fseek(fp, 0, SEEK_END);
    length = ftell(fp);
    fseek(fp, 0, SEEK_SET);
    buffer = malloc(length);
    if (buffer) {
      fread(buffer, 1, length, fp);
    }
    fclose(fp);
  }
 
  if (buffer) {
    strcpy(badbuffer, buffer);
    printf("%s", badbuffer);
  }
 
}
