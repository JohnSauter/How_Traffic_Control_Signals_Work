/*
* Program to write a checkerboard image as a PNG file..
*/
#include <stdlib.h>
#include <getopt.h>		/* getopt_long() */
#include <errno.h>
#include <string.h>
#include <malloc.h>

#include <png.h>

static char *output_file = NULL;
static int png_compression_level_value = 6;
static int debug_level = 0;
static int checkerboard_size = 1024;
static int random_bits = 0;
static int random_mask = 0;
static int checkerboard_incr = 1;

/* routine to exit with an error message */
static void
errno_exit (const char *s)
{
  fprintf (stderr, "%s error %d, %s\n", s, errno, strerror (errno));
  exit (EXIT_FAILURE);
}

/* routine to create a random value limited to low-order bits */
static int
random_val ()
{
  int return_val;
  return_val = rand () & random_mask;
  return return_val;
}

/* Subroutine to create a checkerboard image and write it as a png file */
static void
write_file (char *output_file_name)
{
  int result;
  long int output_buffer_size;
  long int pixel_count;
  long int row_pixels;
  
  row_pixels = (long int) checkerboard_size * (long int) checkerboard_incr;
  pixel_count = (long int) row_pixels * (long int) row_pixels;
  output_buffer_size = pixel_count * 3;
  unsigned char *output_buffer;
  output_buffer = malloc (output_buffer_size);
  if (output_buffer == NULL)
    {
      fprintf (stderr, "Unable to allocate output buffer of %ld bytes.\n",
	       output_buffer_size);
      exit (EXIT_FAILURE);
    }

/*
 * Create the checkerboard.  The PNG file is in RGB format, so we store
 * the colur three times: once for red, once for green and once
 * for blue.  Note that the randomness is applied separately to each
 * color and to each pixel within a square.
 */
  int color, row, column, x_pixel, y_pixel;
  long long int x_ptr, y_ptr, buffer_pointer;
  
  for (row = 0; row < checkerboard_size; row++)
    {
      for (column = 0; column < checkerboard_size; column++)
	{
	  color = (row ^ column) & 1;

	  /* Each square is checkerboard_incr by checkerboard incr pixels.  */
	  for (x_pixel = 0; x_pixel < checkerboard_incr; x_pixel++)
	    {
	      for (y_pixel = 0; y_pixel < checkerboard_incr; y_pixel++)
		{
		  x_ptr = (row * checkerboard_incr) + x_pixel;
		  y_ptr = (column * checkerboard_incr) + y_pixel;
		  buffer_pointer = (3LL *
				    ((x_ptr *
				      (checkerboard_size * checkerboard_incr)) +
				     y_ptr));
		  switch (color)
		    {
		    case 0:
		      output_buffer[buffer_pointer] = random_val ();
		      output_buffer[buffer_pointer + 1] = random_val ();
		      output_buffer[buffer_pointer + 2] = random_val ();
		      break;
		    case 1:
		      output_buffer[buffer_pointer] = 255 ^ random_val ();
		      output_buffer[buffer_pointer + 1] = 255 ^ random_val ();
		      output_buffer[buffer_pointer + 2] = 255 ^ random_val ();
		      break;
		    }
		}
	    }
	}
    }

/*
 * Write the image.
 */
  FILE *fp;
  fp = fopen (output_file_name, "wb");
  if (!fp)
    {
      fprintf (stderr, "File: %s\n", output_file_name);
      errno_exit ("Opening png file.");
    }
  png_structp png_ptr = png_create_write_struct
    (PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
  if (!png_ptr)
    {
      fprintf (stderr, "Unable to allocate png write structure.\n");
      exit (EXIT_FAILURE);
    }
  png_infop info_ptr = png_create_info_struct (png_ptr);
  if (!info_ptr)
    {
      png_destroy_write_struct (&png_ptr, (png_infopp) NULL);
      fprintf (stderr, "Unable to allocate png info structure.\n");
      exit (EXIT_FAILURE);
    }
  if (setjmp (png_jmpbuf (png_ptr)))
    {
      fprintf (stderr, "Error during png file processing.\n");
      png_destroy_write_struct (&png_ptr, &info_ptr);
      fclose (fp);
      exit (EXIT_FAILURE);
    }
  png_init_io (png_ptr, fp);
  png_set_IHDR (png_ptr, info_ptr, checkerboard_size * checkerboard_incr,
		checkerboard_size * checkerboard_incr, 8,
		PNG_COLOR_TYPE_RGB, PNG_INTERLACE_NONE,
		PNG_COMPRESSION_TYPE_DEFAULT, PNG_FILTER_TYPE_DEFAULT);
  png_set_compression_level (png_ptr, png_compression_level_value);
  if (checkerboard_size > PNG_UINT_32_MAX / sizeof (png_byte))
    png_error (png_ptr, "Image is too tall to process in memory");
  if ((checkerboard_size * checkerboard_incr) > PNG_UINT_32_MAX / 3)
    png_error (png_ptr, "Image is too wide to process in memory");
  png_bytep *row_pointers;
  row_pointers = png_malloc (png_ptr,
			     (long int) sizeof (png_bytep) *
			     (long int) checkerboard_size * checkerboard_incr);
  if (row_pointers == NULL)
    {
      fprintf (stderr, "Unable to allocate row pointers: %ld bytes.\n",
	       sizeof (png_bytep) * checkerboard_size * checkerboard_incr);
      png_destroy_write_struct (&png_ptr, &info_ptr);
      fclose (fp);
      exit (EXIT_FAILURE);
    }
  long int row_no;
  for (row_no = 0; row_no < checkerboard_size * checkerboard_incr; row_no++)
    row_pointers[row_no] =
      &output_buffer[row_no * (long int) (checkerboard_size *
					  checkerboard_incr * 3)];
  png_set_rows (png_ptr, info_ptr, &row_pointers[0]);
  png_write_png (png_ptr, info_ptr, 0, NULL);
  png_destroy_write_struct (&png_ptr, &info_ptr);
  free (output_buffer);
  result = fclose (fp);
  if (result != 0)
    {
      fprintf (stderr, "File: %s\n", output_file_name);
      errno_exit ("closing png file");
    }
}

static void
usage (FILE * fp, int argc, char **argv)
{
  fprintf (fp,
	   "Usage: %s [options]\n\n"
	   "\n"
	   "Write a checkerboard image in png format.\n"
	   " Version 3.0 2020-09-17\n"
	   "\n"
	   "Options:\n"
	   "-h | --help          Print this message\n"
	   "-o | --output-file   Where to put the png file\n"
	   "-p | --png-compression-level space vs speed, 0-9, default 3\n"
	   "-s | --size          Size of the checkerboard, in squares\n"
	   "-r | --random        Random bits to add to each check, 0-8\n"
	   "-i | --increment     Size of each square, in pixels\n"
	   "-D | --debug-level   Amount of debugging output, default 0\n"
	   "", argv[0]);
}

static const char short_options[] = "ho:p:s:r:i:D:";

static const struct option long_options[] = {
  {"help", no_argument, NULL, 'h'},
  {"output-file", required_argument, NULL, 'o'},
  {"png-compression-level", required_argument, NULL, 'p'},
  {"size", required_argument, NULL, 's'},
  {"random", required_argument, NULL, 'r'},
  {"increment", required_argument, NULL, 'i'},
  {"debug-level", required_argument, NULL, 'D'},
  {0, 0, 0, 0}
};

/* main program: parse options, create file, exit. */
int
main (int argc, char **argv)
{

  for (;;)
    {
      int index;
      int c;
      
      c = getopt_long (argc, argv, short_options, long_options, &index);

      if (-1 == c)
	break;

      switch (c)
	{
	case 0:		/* getopt_long() flag */
	  break;

	case 'h':
	  usage (stdout, argc, argv);
	  exit (EXIT_SUCCESS);

	case 'o':
	  output_file = optarg;
	  break;

	case 'p':
	  png_compression_level_value = atoi (optarg);
	  break;

	case 's':
	  checkerboard_size = atoi (optarg);
	  break;

	case 'r':
	  random_bits = atoi (optarg);
	  random_mask = (1 << (random_bits + 1)) - 1;
	  break;

	case 'i':
	  checkerboard_incr = atoi (optarg);
	  break;	   

	case 'D':
	  debug_level = atoi (optarg);
	  break;

	default:
	  usage (stderr, argc, argv);
	  exit (EXIT_FAILURE);
	}
    }

  if (output_file == NULL)
    {
      fprintf (stderr, "The output file must be specified.\n");
      exit (EXIT_FAILURE);
    }
  write_file (output_file);
  exit (EXIT_SUCCESS);

  return 0;
}
