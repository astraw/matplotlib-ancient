/*
 * Modified for use within matplotlib
 * 5 July 2007
 * Michael Droettboom
 */

/*
** ~ppr/src/pprdrv/pprdrv_tt2.c
** Copyright 1995, Trinity College Computing Center.
** Written by David Chappell.
**
** Permission to use, copy, modify, and distribute this software and its
** documentation for any purpose and without fee is hereby granted, provided
** that the above copyright notice appear in all copies and that both that
** copyright notice and this permission notice appear in supporting
** documentation.  This software is provided "as is" without express or
** implied warranty.
**
** TrueType font support.  These functions allow PPR to generate
** PostScript fonts from Microsoft compatible TrueType font files.
**
** The functions in this file do most of the work to convert a
** TrueType font to a type 3 PostScript font.
**
** Most of the material in this file is derived from a program called
** "ttf2ps" which L. S. Ng posted to the usenet news group
** "comp.sources.postscript".  The author did not provide a copyright
** notice or indicate any restrictions on use.
**
** Last revised 11 July 1995.
*/

#include "global_defines.h"
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <memory>
#include "pprdrv.h"
#include "truetype.h"
#include <algorithm>
#include <stack>

class GlyphToType3 {
private:
    GlyphToType3& operator=(const GlyphToType3& other);
    GlyphToType3(const GlyphToType3& other);

    /* The PostScript bounding box. */
    int llx,lly,urx,ury;
    int advance_width;

    /* Variables to hold the character data. */
    int *epts_ctr;			/* array of contour endpoints */
    int num_pts, num_ctr;		/* number of points, number of coutours */
    FWord *xcoor, *ycoor;		/* arrays of x and y coordinates */
    BYTE *tt_flags;			/* array of TrueType flags */
    double *area_ctr;
    char *check_ctr;
    int *ctrset;  		/* in contour index followed by out contour index */

    int stack_depth;            /* A book-keeping variable for keeping track of the depth of the PS stack */

    bool pdf_mode;

    void load_char(TTFONT* font, BYTE *glyph);
    void stack(TTStreamWriter& stream, int new_elem);
    void stack_end(TTStreamWriter& stream);
    void PSConvert(TTStreamWriter& stream);
    int nextinctr(int co, int ci);
    int nextoutctr(int co);
    int nearout(int ci);
    double intest(int co, int ci);
    void PSCurveto(TTStreamWriter& stream, FWord x, FWord y, int s, int t);
    void PSMoveto(TTStreamWriter& stream, int x, int y);
    void PSLineto(TTStreamWriter& stream, int x, int y);
    void do_composite(TTStreamWriter& stream, struct TTFONT *font, BYTE *glyph);

public:
    GlyphToType3(TTStreamWriter& stream, struct TTFONT *font, int charindex, bool embedded = false);
    ~GlyphToType3();
};

double area(FWord *x, FWord *y, int n);
#define sqr(x) ((x)*(x))

#define NOMOREINCTR -1
#define NOMOREOUTCTR -1

/*
** This routine is used to break the character
** procedure up into a number of smaller
** procedures.  This is necessary so as not to
** overflow the stack on certain level 1 interpreters.
**
** Prepare to push another item onto the stack,
** starting a new proceedure if necessary.
**
** Not all the stack depth calculations in this routine
** are perfectly accurate, but they do the job.
*/
void GlyphToType3::stack(TTStreamWriter& stream, int new_elem)
    {
    if( !pdf_mode && num_pts > 25 )			/* Only do something of we will */
	{				/* have a log of points. */
	if(stack_depth == 0)
	    {
    	    stream.put_char('{');
    	    stack_depth=1;
    	    }

	stack_depth += new_elem;		/* Account for what we propose to add */

	if(stack_depth > 100)
    	    {
    	    stream.puts("}_e{");
    	    stack_depth = 3 + new_elem;	/* A rough estimate */
    	    }
    	}
    } /* end of stack() */

void GlyphToType3::stack_end(TTStreamWriter& stream)			/* called at end */
    {
    if( !pdf_mode && stack_depth )
    	{
    	stream.puts("}_e");
    	stack_depth=0;
    	}
    } /* end of stack_end() */

/*
** Find the area of a contour?
*/
double area(FWord *x, FWord *y, int n)
     {
     int i;
     double sum;

     sum=x[n-1]*y[0]-y[n-1]*x[0];
     for (i=0; i<=n-2; i++) sum += x[i]*y[i+1] - y[i]*x[i+1];
     return sum;
     }

/*
** We call this routine to emmit the PostScript code
** for the character we have loaded with load_char().
*/
void GlyphToType3::PSConvert(TTStreamWriter& stream)
    {
    int i,j,k,fst,start_offpt;
    int end_offpt = 0;

    assert(area_ctr == NULL);
    area_ctr=(double*)calloc(num_ctr, sizeof(double));
    memset(area_ctr, 0, (num_ctr*sizeof(double)));
    assert(check_ctr == NULL);
    check_ctr=(char*)calloc(num_ctr, sizeof(char));
    memset(check_ctr, 0, (num_ctr*sizeof(char)));
    assert(ctrset == NULL);
    ctrset=(int*)calloc(num_ctr, 2*sizeof(int));
    memset(ctrset, 0, (num_ctr*2*sizeof(int)));

    check_ctr[0]=1;
    area_ctr[0]=area(xcoor, ycoor, epts_ctr[0]+1);

    for (i=1; i<num_ctr; i++)
     	area_ctr[i]=area(xcoor+epts_ctr[i-1]+1, ycoor+epts_ctr[i-1]+1, epts_ctr[i]-epts_ctr[i-1]);

    for (i=0; i<num_ctr; i++)
	{
     	if (area_ctr[i]>0)
	    {
	    ctrset[2*i]=i; ctrset[2*i+1]=nearout(i);
	    }
	else
	    {
	    ctrset[2*i]=-1; ctrset[2*i+1]=-1;
	    }
	}

    /* Step thru the coutours. */
    /* I believe that a contour is a detatched */
    /* set of curves and lines. */
    i=j=k=0;
    while( i < num_ctr )
	{
	fst = j = (k==0) ? 0 : (epts_ctr[k-1]+1);

	/* Move to the first point on the contour. */
	stack(stream, 3);
	PSMoveto(stream,xcoor[j],ycoor[j]);

	start_offpt = 0;		/* No off curve points yet. */

	/* Step thru the remaining points of this contour. */
	for(j++; j <= epts_ctr[k]; j++)
	    {
	    if (!(tt_flags[j]&1))	/* Off curve */
		{
		if (!start_offpt)
		    { start_offpt = end_offpt = j; }
		else
		    end_offpt++;
		}
	    else
		{			/* On Curve */
		if (start_offpt)
		    {
		    stack(stream, 7);
		    PSCurveto(stream, xcoor[j],ycoor[j],start_offpt,end_offpt);
		    start_offpt = 0;
		    }
		else
		    {
                    stack(stream, 3);
		    PSLineto(stream, xcoor[j], ycoor[j]);
		    }
		}
	    }

	/* Do the final curve or line */
	/* of this coutour. */
	if (start_offpt)
	    {
	      stack(stream, 7); PSCurveto(stream, xcoor[fst],ycoor[fst],start_offpt,end_offpt);
	    }
	else
	    {
	      stack(stream, 3); PSLineto(stream, xcoor[fst],ycoor[fst]);
	    }

	k=nextinctr(i,k);

	if (k==NOMOREINCTR)
	    i=k=nextoutctr(i);

	 if (i==NOMOREOUTCTR)
	     break;
	 }

    /* Now, we can fill the whole thing. */
    stack(stream, 1);
    stream.puts( pdf_mode ? "f" : "_cl" );

    /* Free our work arrays. */
    free(area_ctr);
    free(check_ctr);
    free(ctrset);
    area_ctr = NULL;
    check_ctr = NULL;
    ctrset = NULL;
    } /* end of PSConvert() */

int GlyphToType3::nextoutctr(int co)
	{
	int j;

	for(j=0; j<num_ctr; j++)
	   if (check_ctr[j]==0 && area_ctr[j] < 0) {
	   	check_ctr[j]=1;
	   	return j;
	   }

	return NOMOREOUTCTR;
	} /* end of nextoutctr() */

int GlyphToType3::nextinctr(int co, int ci)
	{
	int j;

	for(j=0; j<num_ctr; j++)
           if (ctrset[2*j+1]==co)
           if (check_ctr[ctrset[2*j]]==0) {
		check_ctr[ctrset[2*j]]=1;
	   	return ctrset[2*j];
	   }

	return NOMOREINCTR;
	}

/*
** find the nearest out contour to a specified in contour.
*/
int GlyphToType3::nearout(int ci)
    {
    int k = 0;			/* !!! is this right? */
    int co;
    double a, a1=0;

    for (co=0; co < num_ctr; co++)
	{
	if(area_ctr[co] < 0)
	    {
	    a=intest(co,ci);
	    if (a<0 && a1==0)
		{
		k=co;
		a1=a;
		}
	    if(a<0 && a1!=0 && a>a1)
		{
		k=co;
		a1=a;
		}
	    }
	}

    return k;
    } /* end of nearout() */

double GlyphToType3::intest(int co, int ci)
	{
	int i, j, start, end;
	double r1, r2, a;
	FWord xi[3], yi[3];

	j=start=(co==0)?0:(epts_ctr[co-1]+1);
	end=epts_ctr[co];
	i=(ci==0)?0:(epts_ctr[ci-1]+1);
	xi[0] = xcoor[i];
	yi[0] = ycoor[i];
	r1=sqr(xcoor[start] - xi[0]) + sqr(ycoor[start] - yi[0]);

	for (i=start; i<=end; i++) {
		r2 = sqr(xcoor[i] - xi[0])+sqr(ycoor[i] - yi[0]);
		if (r2 < r1) {
			r1=r2; j=i;
		}
	}
	xi[1]=xcoor[j-1]; yi[1]=ycoor[j-1];
	xi[2]=xcoor[j+1]; yi[2]=ycoor[j+1];
        if (j==start) { xi[1]=xcoor[end]; yi[1]=ycoor[end]; }
	if (j==end) { xi[2]=xcoor[start]; yi[2]=ycoor[start]; }
	a=area(xi, yi, 3);

	return a;
	} /* end of intest() */

void GlyphToType3::PSMoveto(TTStreamWriter& stream, int x, int y) {
    stream.printf(pdf_mode ? "%d %d m\n" : "%d %d _m\n",
		  x, y);
}

void GlyphToType3::PSLineto(TTStreamWriter& stream, int x, int y) {
    stream.printf(pdf_mode ? "%d %d l\n" : "%d %d _l\n",
		  x, y);
}

/*
** Emmit a PostScript "curveto" command.
*/
void GlyphToType3::PSCurveto(TTStreamWriter& stream, FWord x, FWord y, int s, int t)
     {
     int N, i;
     double sx[3], sy[3], cx[4], cy[4];

     N = t-s+2;
     for(i=0; i<N-1; i++)
	{
	sx[0] = i==0?xcoor[s-1]:(xcoor[i+s]+xcoor[i+s-1])/2;
	sy[0] = i==0?ycoor[s-1]:(ycoor[i+s]+ycoor[i+s-1])/2;
	sx[1] = xcoor[s+i];
	sy[1] = ycoor[s+i];
	sx[2] = i==N-2?x:(xcoor[s+i]+xcoor[s+i+1])/2;
	sy[2] = i==N-2?y:(ycoor[s+i]+ycoor[s+i+1])/2;
	cx[3] = sx[2];
	cy[3] = sy[2];
	cx[1] = (2*sx[1]+sx[0])/3;
	cy[1] = (2*sy[1]+sy[0])/3;
	cx[2] = (sx[2]+2*sx[1])/3;
	cy[2] = (sy[2]+2*sy[1])/3;

	stream.printf(pdf_mode ?
		         "%d %d %d %d %d %d c\n" :
		         "%d %d %d %d %d %d _c\n",
		      (int)cx[1], (int)cy[1], (int)cx[2], (int)cy[2],
		      (int)cx[3], (int)cy[3]);
	}
     } /* end of PSCurveto() */

/*
** Deallocate the structures which stored
** the data for the last simple glyph.
*/
GlyphToType3::~GlyphToType3() {
     free(tt_flags);		/* The flags array */
     free(xcoor);		/* The X coordinates */
     free(ycoor);		/* The Y coordinates */
     free(epts_ctr);		/* The array of contour endpoints */
     // These last three should be NULL.  Just
     // free'ing them for safety.
     free(area_ctr);
     free(check_ctr);
     free(ctrset);
}

/*
** Load the simple glyph data pointed to by glyph.
** The pointer "glyph" should point 10 bytes into
** the glyph data.
*/
void GlyphToType3::load_char(TTFONT* font, BYTE *glyph)
    {
    int x;
    BYTE c, ct;

    /* Read the contour endpoints list. */
    epts_ctr = (int *)calloc(num_ctr,sizeof(int));
    for (x = 0; x < num_ctr; x++)
    	{
    	epts_ctr[x] = getUSHORT(glyph);
    	glyph += 2;
    	}

    /* From the endpoint of the last contour, we can */
    /* determine the number of points. */
    num_pts = epts_ctr[num_ctr-1]+1;
    #ifdef DEBUG_TRUETYPE
    debug("num_pts=%d",num_pts);
    stream.printf("%% num_pts=%d\n",num_pts);
    #endif

    /* Skip the instructions. */
    x = getUSHORT(glyph);
    glyph += 2;
    glyph += x;

    /* Allocate space to hold the data. */
    tt_flags = (BYTE *)calloc(num_pts,sizeof(BYTE));
    xcoor = (FWord *)calloc(num_pts,sizeof(FWord));
    ycoor = (FWord *)calloc(num_pts,sizeof(FWord));

    /* Read the flags array, uncompressing it as we go. */
    /* There is danger of overflow here. */
    for (x = 0; x < num_pts; )
	{
	tt_flags[x++] = c = *(glyph++);

	if (c&8)		/* If next byte is repeat count, */
	    {
	    ct = *(glyph++);

	    if( (x + ct) > num_pts )
		throw TTException("Error in TT flags");

	    while (ct--)
		tt_flags[x++] = c;
	    }
	}

    /* Read the x coordinates */
    for (x = 0; x < num_pts; x++)
	{
	if (tt_flags[x] & 2)		/* one byte value with */
	    {				/* external sign */
	    c = *(glyph++);
	    xcoor[x] = (tt_flags[x] & 0x10) ? c : (-1 * (int)c);
	    }
	else if(tt_flags[x] & 0x10)	/* repeat last */
	    {
	    xcoor[x] = 0;
	    }
	else				/* two byte signed value */
	    {
	    xcoor[x] = getFWord(glyph);
	    glyph+=2;
	    }
	}

    /* Read the y coordinates */
    for(x = 0; x < num_pts; x++)
	{
	if (tt_flags[x] & 4)		/* one byte value with */
	    {				/* external sign */
	    c = *(glyph++);
	    ycoor[x] = (tt_flags[x] & 0x20) ? c : (-1 * (int)c);
	    }
	else if (tt_flags[x] & 0x20)	/* repeat last value */
	     {
	     ycoor[x] = 0;
	     }
	else				/* two byte signed value */
	     {
	     ycoor[x] = getUSHORT(glyph);
	     glyph+=2;
	     }
	 }

     /* Convert delta values to absolute values. */
     for(x = 1; x < num_pts; x++)
	{
	xcoor[x] += xcoor[x-1];
	ycoor[x] += ycoor[x-1];
	}

     for(x=0; x < num_pts; x++)
	{
	xcoor[x] = topost(xcoor[x]);
	ycoor[x] = topost(ycoor[x]);
	}

     } /* end of load_char() */

/*
** Emmit PostScript code for a composite character.
*/
void GlyphToType3::do_composite(TTStreamWriter& stream, struct TTFONT *font, BYTE *glyph)
    {
    USHORT flags;
    USHORT glyphIndex;
    int arg1;
    int arg2;
    USHORT xscale;
    USHORT yscale;
    USHORT scale01;
    USHORT scale10;

    /* Once around this loop for each component. */
    do	{
	flags = getUSHORT(glyph);	/* read the flags word */
	glyph += 2;

	glyphIndex = getUSHORT(glyph);	/* read the glyphindex word */
	glyph += 2;

	if(flags & ARG_1_AND_2_ARE_WORDS)
	    {			/* The tt spec. seems to say these are signed. */
	    arg1 = getSHORT(glyph);
	    glyph += 2;
	    arg2 = getSHORT(glyph);
	    glyph += 2;
	    }
    	else			/* The tt spec. does not clearly indicate */
    	    {			/* whether these values are signed or not. */
              arg1 = *(signed char *)(glyph++);
              arg2 = *(signed char *)(glyph++);
	    }

	if(flags & WE_HAVE_A_SCALE)
	    {
	    xscale = yscale = getUSHORT(glyph);
	    glyph += 2;
	    scale01 = scale10 = 0;
	    }
	else if(flags & WE_HAVE_AN_X_AND_Y_SCALE)
	    {
	    xscale = getUSHORT(glyph);
	    glyph += 2;
	    yscale = getUSHORT(glyph);
	    glyph += 2;
	    scale01 = scale10 = 0;
	    }
	else if(flags & WE_HAVE_A_TWO_BY_TWO)
	    {
	    xscale = getUSHORT(glyph);
	    glyph += 2;
	    scale01 = getUSHORT(glyph);
	    glyph += 2;
	    scale10 = getUSHORT(glyph);
	    glyph += 2;
	    yscale = getUSHORT(glyph);
	    glyph += 2;
	    }
	else
	    {
	    xscale = yscale = scale01 = scale10 = 0;
	    }

	/* Debugging */
	#ifdef DEBUG_TRUETYPE
	stream.printf("%% flags=%d, arg1=%d, arg2=%d, xscale=%d, yscale=%d, scale01=%d, scale10=%d\n",
		(int)flags,arg1,arg2,(int)xscale,(int)yscale,(int)scale01,(int)scale10);
	#endif

	if (pdf_mode) {
	    if ( flags & ARGS_ARE_XY_VALUES ) {
		/* We should have been able to use 'Do' to reference the
		   subglyph here.  However, that doesn't seem to work with
		   xpdf or gs (only acrobat), so instead, this just includes
		   the subglyph here inline. */
		stream.printf("q 1 0 0 1 %d %d cm\n", topost(arg1), topost(arg2));
	    } else {
		    stream.printf("%% unimplemented shift, arg1=%d, arg2=%d\n",arg1,arg2);
	    }
	    GlyphToType3(stream, font, glyphIndex, true);
	    if ( flags & ARGS_ARE_XY_VALUES ) {
		stream.printf("\nQ\n");
	    }
	} else {
	    /* If we have an (X,Y) shif and it is non-zero, */
	    /* translate the coordinate system. */
	    if( flags & ARGS_ARE_XY_VALUES )
		{
		    if( arg1 != 0 || arg2 != 0 )
			stream.printf("gsave %d %d translate\n", topost(arg1), topost(arg2) );
		}
	    else
		{
		    stream.printf("%% unimplemented shift, arg1=%d, arg2=%d\n",arg1,arg2);
		}

	    /* Invoke the CharStrings procedure to print the component. */
	    stream.printf("false CharStrings /%s get exec\n",
			  ttfont_CharStrings_getname(font,glyphIndex));

	    /* If we translated the coordinate system, */
	    /* put it back the way it was. */
	    if( flags & ARGS_ARE_XY_VALUES && (arg1 != 0 || arg2 != 0) ) {
		stream.puts("grestore ");
	    }
	}

	} while(flags & MORE_COMPONENTS);

    } /* end of do_composite() */

/*
** Return a pointer to a specific glyph's data.
*/
BYTE *find_glyph_data(struct TTFONT *font, int charindex)
    {
    ULONG off;
    ULONG length;

    /* Read the glyph offset from the index to location table. */
    if(font->indexToLocFormat == 0)
	{
	off = getUSHORT( font->loca_table + (charindex * 2) );
	off *= 2;
	length = getUSHORT( font->loca_table + ((charindex+1) * 2) );
	length *= 2;
	length -= off;
	}
    else
	{
	off = getULONG( font->loca_table + (charindex * 4) );
	length = getULONG( font->loca_table + ((charindex+1) * 4) );
	length -= off;
	}

    if(length > 0)
    	return font->glyf_table + off;
    else
    	return (BYTE*)NULL;

    } /* end of find_glyph_data() */

GlyphToType3::GlyphToType3(TTStreamWriter& stream, struct TTFONT *font, int charindex, bool embedded /* = false */) {
    BYTE *glyph;

    tt_flags = NULL;
    xcoor = NULL;
    ycoor = NULL;
    epts_ctr = NULL;
    area_ctr = NULL;
    check_ctr = NULL;
    ctrset = NULL;
    stack_depth = 0;
    pdf_mode = font->target_type < 0;

    /* Get a pointer to the data. */
    glyph = find_glyph_data( font, charindex );

    /* If the character is blank, it has no bounding box, */
    /* otherwise read the bounding box. */
    if( glyph == (BYTE*)NULL )
    	{
	llx=lly=urx=ury=0;	/* A blank char has an all zero BoundingBox */
	num_ctr=0;		/* Set this for later if()s */
    	}
    else
	{
	/* Read the number of contours. */
	num_ctr = getSHORT(glyph);

	/* Read PostScript bounding box. */
	llx = getFWord(glyph + 2);
	lly = getFWord(glyph + 4);
	urx = getFWord(glyph + 6);
	ury = getFWord(glyph + 8);

	/* Advance the pointer. */
	glyph += 10;
	}

    /* If it is a simple character, load its data. */
    if (num_ctr > 0)
	load_char(font, glyph);
    else
        num_pts=0;

    /* Consult the horizontal metrics table to determine */
    /* the character width. */
    if( charindex < font->numberOfHMetrics )
	advance_width = getuFWord( font->hmtx_table + (charindex * 4) );
    else
    	advance_width = getuFWord( font->hmtx_table + ((font->numberOfHMetrics-1) * 4) );

    /* Execute setcachedevice in order to inform the font machinery */
    /* of the character bounding box and advance width. */
    stack(stream, 7);
    if (pdf_mode) {
	if (!embedded)
	    stream.printf("%d 0 %d %d %d %d d1\n",
			  topost(advance_width),
			  topost(llx), topost(lly), topost(urx), topost(ury) );
    } else
	stream.printf("%d 0 %d %d %d %d _sc\n",
		      topost(advance_width),
		      topost(llx), topost(lly), topost(urx), topost(ury) );

    /* If it is a simple glyph, convert it, */
    /* otherwise, close the stack business. */
    if( num_ctr > 0 )		/* simple */
	{
        PSConvert(stream);
	}
    else if( num_ctr < 0 )	/* composite */
	{
	  do_composite(stream, font, glyph);
	}

    stack_end(stream);
}

/*
** This is the routine which is called from pprdrv_tt.c.
*/
void tt_type3_charproc(TTStreamWriter& stream, struct TTFONT *font, int charindex)
    {
      GlyphToType3 glyph(stream, font, charindex);
} /* end of tt_type3_charproc() */

/*
** Some of the given glyph ids may refer to composite glyphs.
** This function adds all of the dependencies of those composite
** glyphs to the glyph id vector.  Michael Droettboom [06-07-07]
*/
void ttfont_add_glyph_dependencies(struct TTFONT *font, std::vector<int>& glyph_ids) {
    std::sort(glyph_ids.begin(), glyph_ids.end());

    std::stack<int> glyph_stack;
    for (std::vector<int>::iterator i = glyph_ids.begin();
	 i != glyph_ids.end(); ++i) {
	glyph_stack.push(*i);
    }

    while (glyph_stack.size()) {
	int gind = glyph_stack.top();
	glyph_stack.pop();

	BYTE* glyph = find_glyph_data( font, gind );
	if (glyph != (BYTE*)NULL) {

	    int num_ctr = getSHORT(glyph);
	    if (num_ctr <= 0) { // This is a composite glyph

		glyph += 10;
		USHORT flags = 0;

		do {
		    flags = getUSHORT(glyph);
		    glyph += 2;
		    gind = (int)getUSHORT(glyph);
		    glyph += 2;

		    std::vector<int>::iterator insertion =
			std::lower_bound(glyph_ids.begin(), glyph_ids.end(), gind);
		    if (*insertion != gind) {
			glyph_ids.insert(insertion, gind);
			glyph_stack.push(gind);
		    }

		    if (flags & ARG_1_AND_2_ARE_WORDS)
			glyph += 4;
		    else
			glyph += 2;

		    if (flags & WE_HAVE_A_SCALE)
			glyph += 2;
		    else if (flags & WE_HAVE_AN_X_AND_Y_SCALE)
			glyph += 4;
		    else if (flags & WE_HAVE_A_TWO_BY_TWO)
			glyph += 8;
		} while (flags & MORE_COMPONENTS);
	    }
	}
    }
}

/* end of file */
