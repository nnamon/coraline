#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char **argv) {
  if (argc < 2) {
    printf("No");
    return 1;
  }
  char * buffer = 0;
  long length;
  FILE * fp = fopen(argv[1], "r");
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

  if (buffer[2] == 0x42) {
    strcpy(badbuffer, buffer);
    printf("%s", badbuffer);
  }
  else if (buffer[2] == 0x43) {
      sleep(20);
  }

  return 0;

}
