folders="rest push walk"
for folder in $folders
do
    cd $folder
    for file in `ls *.obj`
    do
        sed -r 's/mirrorman_0000[0-9][0-9]/..\/mirrorman/g' -i $file
    done
    rm *.mtl
    cd ..
done
