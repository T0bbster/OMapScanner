def draw_boxes(image, bounds, color='red', width=2):
    draw = ImageDraw.Draw(image)
    for bound in bounds:
        p0, p1, p2, p3 = bound[0]
        draw.line([*p0, *p1, *p2, *p3, *p0], fill=color, width=width)


def draw_boxes_on_image(reader, in_path, out_dir):
    fp = Path(in_path)
    bounds = reader.readtext(in_path)
    image = PIL.Image.open(in_path)
    draw_boxes(image, bounds)
    image.save(os.path.join(out_dir, fp.stem + '.out' + fp.suffix))


def tmp():
    print(f'Scanning files in directory: \'{parsed_args.directory}\'')
    failed_files = []
    for root, _, files in os.walk(parsed_args.directory):
        for filename in files:
            try:
                print(f'\tScanning {filename}', end='\r')
                time_start = time()
                draw_boxes_on_image(reader, root + '/' + filename, out_dir)
                time_end = time()
                print(f'\tScanned  {filename} in {time_end - time_start:2.4f} sec')
            except Exception as exc:
                logging.error(f'Scanning {filename} failed: ', exc_info=exc)
                failed_files.append(filename)
    
    print('Failed to scan the following files:')
    for file in failed_files:
        print(f'\t{file}')