PREFIX='emitter-explode'
for f in `ls ${PREFIX}*.obj`
do
    sed -r "s/mtllib ${PREFIX}_000[0-9][0-9][0-9]\.mtl/mtllib ${PREFIX}.mtl/g" -i $f 
done
for f in `ls ${PREFIX}*.mtl`
do
    mv $f $PREFIX.mtl
done
